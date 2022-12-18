import mujoco
#@title Other imports and helper functions
import numpy as np
from typing import Callable, Optional, Union, List
import scipy.linalg
import mediapy as media
import matplotlib.pyplot as plt

# More legible printing from numpy.
np.set_printoptions(precision=3, suppress=True, linewidth=100)

class Renderer:
  """Renders MuJoCo scenes."""

  def __init__(
      self,
      model: mujoco.MjModel,
      height: int = 240,
      width: int = 320,
      max_geom: int = 5000,
  ) -> None:
    """Initializes a new `Renderer`.

    Args:
      model: an MjModel instance.
      height: image height in pixels.
      width: image width in pixels.
      max_geom: integer specifying the maximum number of geoms that can be
        rendered in the same scene.

    Raises:
      ValueError: If `camera_id` is outside the valid range, or if `width` or
        `height` exceed the dimensions of MuJoCo's offscreen framebuffer.
    """


    
    
    buffer_width = model.vis.global_.offwidth
    buffer_height = model.vis.global_.offheight
    if width > buffer_width:
      raise ValueError('Image width {} > framebuffer width {}. Either reduce '
                       'the image width or specify a larger offscreen '
                       'framebuffer in the model XML using the clause\n'
                       '<visual>\n'
                       '  <global offwidth="my_width"/>\n'
                       '</visual>'.format(width, buffer_width))
    if height > buffer_height:
      raise ValueError('Image height {} > framebuffer height {}. Either reduce '
                       'the image height or specify a larger offscreen '
                       'framebuffer in the model XML using the clause\n'
                       '<visual>\n'
                       '  <global offheight="my_height"/>\n'
                       '</visual>'.format(height, buffer_height))

    self._width = width
    self._height = height
    self._model = model

    self._scene = mujoco.MjvScene(model=model, maxgeom=max_geom)
    self._scene_option = mujoco.MjvOption()

    self._rect = mujoco.MjrRect(0, 0, self._width, self._height)

    # Internal buffers.
    self._rgb_buffer = np.empty((self._height, self._width, 3), dtype=np.uint8)
    self._depth_buffer = np.empty((self._height, self._width), dtype=np.float32)

    # Create render contexts.
    self._gl_context = mujoco.GLContext(self._width, self._height)
    self._gl_context.make_current()
    self._mjr_context = mujoco.MjrContext(
        model, mujoco.mjtFontScale.mjFONTSCALE_150
    )
    mujoco.mjr_setBuffer(
        mujoco.mjtFramebuffer.mjFB_OFFSCREEN, self._mjr_context
    )

  def render(self) -> np.ndarray:
    """Renders the scene as a numpy array of pixel values.

    Returns:
      A numpy array of pixels with dimensions (H, W, 3). The array will be
      mutated by future calls to `render`.
    """
    self._gl_context.make_current()

    # Render scene and read contents of RGB buffer.
    mujoco.mjr_render(self._rect, self._scene, self._mjr_context)
    mujoco.mjr_readPixels(self._rgb_buffer, None, self._rect, self._mjr_context)

    pixels = self._rgb_buffer
    return np.flipud(pixels)

  def update_scene(
      self,
      data: mujoco.MjData,
      camera: Union[int, str, mujoco.MjvCamera] = -1,
      scene_option: Optional[mujoco.MjvOption] = None,
    ):
    """Updates geometry used for rendering.

    Args:
      data: An instance of `mujoco.MjData`.
      camera: An instance of `mujoco.MjvCamera`, a string or an integer
      scene_option: A custom `mujoco.MjvOption` instance to use to render
        the scene instead of the default.
    """
    if not isinstance(camera, mujoco.MjvCamera):
      camera_id = camera
      if isinstance(camera_id, str):
        camera_id = self._model.name2id(camera_id, 'camera')
      if camera_id < -1:
        raise ValueError('camera_id cannot be smaller than -1.')
      if camera_id >= self._model.ncam:
        raise ValueError(
            f'model has {self._model.ncam} fixed cameras. '
            f'camera_id={camera_id} is invalid.'
        )
      camera = mujoco.MjvCamera()
      camera.fixedcamid = camera_id

      # -1 corresponds to free camera.
      if camera_id == -1:
        camera.type = mujoco.mjtCamera.mjCAMERA_FREE
        mujoco.mjv_defaultFreeCamera(self._model, camera)
      # Else index into the corresponding fixed camera.
      else:
        camera.type = mujoco.mjtCamera.mjCAMERA_FIXED

    scene_option = scene_option or self._scene_option
    mujoco.mjv_updateScene(
        self._model,
        data,
        scene_option,
        None,
        camera, mujoco.mjtCatBit.mjCAT_ALL,
        self._scene,
    )

  @property
  def scene(self) -> mujoco.MjvScene:
    return self._scene