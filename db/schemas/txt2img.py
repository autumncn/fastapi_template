from typing import List, Optional, Union, Dict
from pydantic import BaseModel


class txt2imgRequest(BaseModel):
    enable_hr: Optional[bool] = False
    denoising_strength: Optional[int] = 0
    firstphase_width: Optional[int] = 0
    firstphase_height: Optional[int] = 0
    hr_scale: Optional[int] = 2
    hr_upscaler: Optional[str] = None
    hr_second_pass_steps: Optional[int] = 0
    hr_resize_x: Optional[int] = 0
    hr_resize_y: Optional[int] = 0
    prompt: str
    styles: Optional[List] = []
    seed: Optional[int] = -1
    subseed: Optional[int] = -1
    subseed_strength: Optional[int] = 0
    seed_resize_from_h: Optional[int] = -1
    seed_resize_from_w: Optional[int] = -1
    sampler_name:  Optional[str]
    batch_size: Optional[int] = 1
    n_iter: Optional[int] = 1
    steps: int = 20
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 512
    restore_faces: Optional[bool] = False
    tiling: Optional[bool] = False
    do_not_save_samples: Optional[bool] = False
    do_not_save_grid: Optional[bool] = False
    negative_prompt: Optional[str] = None
    eta: Optional[int] = 0
    s_churn: Optional[int] = 0
    s_tmax: Optional[int] = 0
    s_tmin: Optional[int] = 0
    s_noise: Optional[int] = 1
    override_settings: Optional[Dict] = {}
    override_settings_restore_afterwards: Optional[bool] = True
    script_args: Optional[List] = []
    sampler_index: Optional[str] = 'Euler'
    script_name: Optional[str] = None
    send_images: bool = True
    save_images: bool = True
    alwayson_scripts: Optional[Dict] = {}

class cnTxt2imgRequest(BaseModel):
    enable_hr: Optional[bool] = False
    denoising_strength: Optional[int] = 0
    firstphase_width: Optional[int] = 0
    firstphase_height: Optional[int] = 0
    hr_scale: Optional[int] = 2
    hr_upscaler: Optional[str] = None
    hr_second_pass_steps: Optional[int] = 0
    hr_resize_x: Optional[int] = 0
    hr_resize_y: Optional[int] = 0
    prompt: str
    styles: Optional[List] = []
    seed: Optional[int] = -1
    subseed: Optional[int] = -1
    subseed_strength: Optional[int] = 0
    seed_resize_from_h: Optional[int] = -1
    seed_resize_from_w: Optional[int] = -1
    sampler_name:  Optional[str]
    batch_size: Optional[int] = 1
    n_iter: Optional[int] = 1
    steps: int = 20
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 512
    restore_faces: Optional[bool] = False
    tiling: Optional[bool] = False
    do_not_save_samples: Optional[bool] = False
    do_not_save_grid: Optional[bool] = False
    negative_prompt: Optional[str] = None
    eta: Optional[int] = 0
    s_churn: Optional[int] = 0
    s_tmax: Optional[int] = 0
    s_tmin: Optional[int] = 0
    s_noise: Optional[int] = 1
    override_settings: Optional[Dict] = {}
    override_settings_restore_afterwards: Optional[bool] = True
    script_args: Optional[List] = []
    sampler_index: Optional[str] = 'Euler'
    script_name: Optional[str] = None
    send_images: bool = True
    save_images: bool = True
    alwayson_scripts: Optional[Dict] = {}



class cnImg2imgRequest(BaseModel):
    init_images: Optional[List] = []
    resize_mode: Optional[int] = 0
    denoising_strength: Optional[float] = 0.75
    image_cfg_scale: Optional[float] = 7.0
    mask: Optional[str] = None
    mask_blur: Optional[int] = 4
    inpainting_fill: Optional[int] = 0
    inpaint_full_res: Optional[bool] = True
    inpaint_full_res_padding: Optional[int] = 0
    inpainting_mask_invert: Optional[int] = 0
    initial_noise_multiplier: Optional[int] = 0
    prompt: Optional[str] = None
    styles: Optional[List] = []
    seed: Optional[int] = -1
    subseed: Optional[int] = -1
    subseed_strength: Optional[int] = 0
    seed_resize_from_h: Optional[int] = -1
    seed_resize_from_w: Optional[int] = -1
    sampler_name: Optional[str] = None
    batch_size: Optional[int] = 1
    n_iter: Optional[int] = 1
    steps: Optional[int] = 20
    cfg_scale: Optional[float] = 7.0
    width: Optional[int] = 512
    height: Optional[int] = 512
    restore_faces: Optional[bool] = False
    tiling: Optional[bool] = False
    do_not_save_samples: Optional[bool] = False
    do_not_save_grid: Optional[bool] = False
    negative_prompt: Optional[str] = None
    eta: Optional[int] = 0
    s_churn: Optional[int] = 0
    s_tmax: Optional[int] = 0
    s_tmin: Optional[int] = 0
    s_noise: Optional[int] = 1
    override_settings: Optional[Dict] = {}
    override_settings_restore_afterwards: Optional[bool] = True
    script_args: Optional[List] = []
    sampler_index: Optional[str] = 'Euler'
    include_init_images: Optional[bool] = False
    script_name: Optional[str] = None
    send_images: Optional[bool] = True
    save_images: Optional[bool] = False
    alwayson_scripts: Optional[Dict] = {}
    controlnet_units: Optional[List] = []

class controlnetRequest(BaseModel):
    input_image: Optional[str] = None
    mask: Optional[str] = None
    module: Optional[str] = None
    model: Optional[str] = None
    weight: Optional[int] = 1
    resize_mode: Optional[str] = None
    lowvram: Optional[bool] = True
    processor_res: Optional[int] = 64
    threshold_a: Optional[int] = 64
    threshold_b: Optional[int] = 64
    guidance: Optional[int] = 1
    guidance_start: Optional[int] = 0
    guidance_end: Optional[int] = 1
    guessmode: Optional[bool] = False
