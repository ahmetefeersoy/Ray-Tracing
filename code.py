#  simpleRT_plugin.py
#
#  Blender add-on for simpleRT render engine
#  a minimal ray tracing engine for CMPE360 Project4&5
#
#  Please read the handout before proceeding!


bl_info = {
    "name": "simple_ray_tracer",
    "description": "Simple Ray-tracer for CMPE360",
    "author": "CMPE360",
    "version": (0, 0, 2023),
    "blender": (3, 5, 1),
    "category": "Render",
}


import bpy
import numpy as np
from mathutils import Vector
from math import sqrt


def ray_cast(scene, origin, direction):
    """wrapper around Blender's Scene.ray_cast() API
    Parameters
    ----------
    scene ： bpy.types.Scene
        The Blender scene we will cast a ray in
    origin : Vector, float array of 3 items
        Origin of the ray
    direction : Vector, float array of 3 items
        Direction of the ray
    Returns
    -------
    has_hit : bool
        The result of the ray cast, i.e. if the ray hits anything in the scene
    hit_loc : Vector, float array of 3 items
        The hit location of this ray cast
    hit_norm : Vector, float array of 3 items
        The face normal at the ray cast hit location
    index : int
        The face index of the hit face of the hit object
        -1 when original data isn’t available
    hit_obj : bpy_types.Object
        The hit object
    matrix: Matrix, float 4 * 4
        The matrix_world of the hit object
    """
    return scene.ray_cast(scene.view_layers[0].depsgraph, origin, direction)


def RT_trace_ray(scene, ray_orig, ray_dir, lights, depth=0):
    """Cast a single ray into the scene
    Parameters
    ----------
    scene : bpy.types.Scene
        The scene that will be rendered
        It stores information about the camera, lights, objects, and material
    ray_orig : Vector, float array of 3 items
        Origin of the current ray
    ray_dir : Vector, float array of 3 items
        Direction of the current ray
    lights : list of bpy_types.Object
        The list of lights in the scene
    depth: int
        The recursion depth of raytracing
        i.e. the number that light bounces in the scene
    Returns
    -------
    color : Vector, float array of 3 items
        Color of the pixel
    """

    # first, we cast a ray into the scene using Blender's built-in function
    has_hit, hit_loc, hit_norm, _, hit_obj, _ = ray_cast(scene, ray_orig, ray_dir)

    # set initial color (black) for the pixel
    color = np.zeros(3)

    # if the ray hits nothing in the scene
    # return initial color (black)
    if not has_hit:
        return color

    # small offset to prevent self-occlusion for secondary rays
    eps = 1e-3
    # ray_cast returns the surface normal of the object geometry
    # this normal may be facing the other way when the ray origin is inside the object
    # here we flip the normal if its wrong, and populate the ray_is_inside variable
    # which will be handy when calculating transmission direction
    ray_inside_object = False
    if hit_norm.dot(ray_dir) > 0:
        hit_norm = -hit_norm
        ray_inside_object = True

    # get the ambient color of the scene
    ambient_color = scene.simpleRT.ambient_color

    # get the material of the object we hit
    mat = hit_obj.simpleRT_material

    # extract the diffuse and specular colors from the material
    # since we only need RGB instead of RGBA,
    # we use .xyz to extract the first three component of the color vector
    diffuse_color = Vector(mat.diffuse_color).xyz
    specular_color = Vector(mat.specular_color).xyz
    # get specular hardness aka the Phong exponent
    specular_hardness = mat.specular_hardness

    # set flag for light hit. Will later be used to apply ambient light
    no_light_hit = True

    # iterate through all the lights in the scene
    for light in lights:
        # get light color
        light_color = np.array(
            light.data.simpleRT_light.color * light.data.simpleRT_light.energy
        )

        # ----------
        # TODO 1: Shadow Ray
        #
        # We cast a shadow ray that begins at the intersection point between our initial ray from the camera
        # and our object. The shadow ray goes towards the direction of the light that we are inspecting in
        # this current iteration of the for-loop. We declared this intersection point hit_loc above, short for
        # hit location. Finish the code below to see if this hit location is in shadow...
        #
        # First, calculate the direction vector from the hit location to the light and call it light_vec.
        # The location of the light can be accessed through light.location.
        light_vec = light.location - hit_loc
        
        # Normalize light_vec and save that as light_dir.
        light_dir = light_vec.normalized()
        
        # Calculate the origin of the shadow ray: new_orig.
        # Remember to account for spurious self-occlusion!
        new_orig = hit_loc + eps * light_dir
        #
        # Cast the shadow ray from the hit location to the light using Blender's ray cast function.
        has_light_hit, _, _, _, _, _ = ray_cast(
            scene, new_orig, light_dir
        )  # DO NOT CHANGE
        #
        # Re-run this script, and render the scene to check your result with Checkpoint 1.
        # If you see black pixels, then you might have done your check for self-occlusion wrong.
        # ----------

        # ----------
        # TODO 2: Blinn-Phong BRDF
        # 
        # If our shadow ray hits something before reaching the light, then we are in the shadow of the light,
        # and the ray_cast function above will return an appropriate boolean in has_light_hit.
        if has_light_hit:
            continue # We are in shadow, so this light will have no contribution to the color.
        # Otherwise, we calculate the color at our intersection point using the Blinn-Phong BRDF model. Let
        else:
        # I represent our color:
        # 
        # I = I_diffuse + I_specular
        #       I_diffuse: diffuse component
        #       I_specular: specular component
        #
        # The diffuse component can be calculated as:
        # I_diffuse = k_diffuse * I_light * (light_dir dot normal_dir)
        #       k_diffuse: intensity of diffuse component, in our case diffuse_color
        #       I_light: intensity of the light, light_color attenuated by inverse-square law
        #       light_dir: direction from the surface point to the light, in our case light_dir
        #       normal_dir: normal at the point on the surface, in our case hit_norm
        #
        # The specular component can be calculated as:
        # I_specular = k_specular * I_light
        #              * (normal_dir dot half_vector)^power
        #       k_specular: intensity of specular component, in our case specular_color
        #       I_light: same as above
        #       normal_dir: same as above
        #       half_vector: halfway vector between the view direction and light direction
        #       power: in our case specular_hardness
        # where:
        #       half_vector = the normalized vector of light_dir + view_dir
        #           light_dir: same as above
        #           view_dir: direction from the surface point to the viewer, the negative of ray_dir
        
        # Calculate intensity of the light, I_light, and scale it inversely by the distance
            I_light = light_color / light_vec.length_squared
        
        # Calculate diffuse component and add that to the pixel color
        #
            diffuse_component = np.array(diffuse_color) * I_light * (np.dot(light_dir,hit_norm))
            color += np.array(diffuse_component) 
 
        #
        # Re-run this script, and render the scene to check your result 
        # ----------
        # Calculate specular component and add that to the pixel color
            half_vector = (light_dir + (-ray_dir))
            half_vector /= np.linalg.norm(half_vector)  # Normalizing the half vector
    
    # I_specular = k_specular * I_light * (normal_dir dot half_vector)^power
            power = specular_hardness  # Adjust to control sharpness of highlights
            specular_component = np.array(specular_color) * I_light * (np.dot(hit_norm, half_vector) ** power)
            color += specular_component

    # Set flag for light hit
            no_light_hit = False

    # ----------
    # TODO 3: AMBIENT
    #
    # If none of the lights hit the object, add the ambient component I_ambient to the pixel color
    # else, pass here. Look at the source code above and do some pattern matching to find the variable
    # that contains our ambient color.
    #
    # I_ambient = k_diffuse * k_ambient
    if no_light_hit:
        #FORMULA IS: ka*Ia where ka: ambient color and Ia: ambient light intensity.
        #print(diffuse_color)
        I_ambient = diffuse_color * Vector(ambient_color)
        color += I_ambient

        return color
    #
    # Re-run this script, and render the scene to check your result with Checkpoint 3.
    # ----------

    # ----------
    # TODO 5: FRESNEL
    #
    # In case we don't use fresnel, get reflectivity k_r directly using:
    reflectivity = mat.mirror_reflectivity
    # Otherwise, calculate k_r using Schlick’s approximation
    if mat.use_fresnel:
        # calculate R_0: R_0 = ((n1 - n2) / (n1 + n2))^2
        # Here n1 is the IOR of air, so n1 = 1
        # n2 is the IOR of the object, you can read it from the material property using: mat.ior
        R_0 = ((1 - mat.ior) / (1 + mat.ior)) ** 2
        theta = abs(ray_dir.dot(hit_norm))
        # 
        # Calculate reflectivity k_r = R_0 + (1 - R_0) (1 - cos(theta))^5 where theta is the incident angle.
        reflectivity = R_0 + (1 - R_0) * (1 - theta) ** 5
    #
    # Re-run this script, and render the scene to check your result with Checkpoint 5.
    # ----------

    # ----------
    # TODO 4: RECURSION AND REFLECTION
    # If the depth is greater than zero, generate a reflected ray from the current x
    # If the depth is greater than zero, generate a reflected ray from the current intersection point using the direction D_reflect to determine the color contribution L_reflect.  
    # Multiply L_reflect by the reflectivity k_r, and then combine the result with the pixel color.
    #
    # Similar to how we handle shadow ray casting, it's important to account for self-occlusion in this context as well.
    # Remember to update depth at the end!
    if depth > 0:
        # Get the direction for reflection ray
        # D_reflect = D - 2 (D dot N) N
        D_reflect = ray_dir - Vector(2 * np.dot(ray_dir, hit_norm) * hit_norm)


        
        # Recursively trace the reflected ray and store the return value as a color L_reflect
        reflect_color = RT_trace_ray(scene, hit_loc + eps * D_reflect, D_reflect, lights, depth - 1)


        
        # Add reflection to the final color: k_r * L_reflect
        color += reflectivity * reflect_color
        #
        # Re-run this script, and render the scene to check your result with Checkpoint 4.
        # ----------

        # ----------
        # TODO 6: TRANSMISSION
        #
        # If the depth is greater than zero, generate a transmitted ray from the current 
        # point of intersection using the direction D_transmit to calculate the color contribution L_transmit. 
        # Multiply this by (1 - k_r) * mat.transmission, and then add the result into the pixel color.
        #
        # Ensure that the refractive indices (n1 and n2) are assigned based on the media through which the ray is passing (as specified by ray_inside_object)
        # Use the refractive index of the object (mat.ior) and set the refractive index of air as 1
        # Proceed with the calculation of D_transmit only if the value under the square root is positive.
        if mat.transmission > 0:
            n1, n2 = (mat.ior, 1) if ray_inside_object else (1, mat.ior)
            n_ratio = n1 / n2
            cos_theta_i = -hit_norm.dot(ray_dir)
            cos_theta_t2 = 1 - n_ratio ** 2 * (1 - cos_theta_i ** 2)
            if cos_theta_t2 >= 0:
                D_transmit = n_ratio * ray_dir + (n_ratio * cos_theta_i - sqrt(cos_theta_t2)) * hit_norm
                transmit_color = RT_trace_ray(scene, hit_loc + eps * D_transmit, D_transmit, lights, depth - 1)
                color += (1 - reflectivity) * mat.transmission * transmit_color
                
    #
    # Re-run this script, and render the scene to check your result with Checkpoint 6.
    # ----------

    return color
    #
    # Re-run this script, and render the scene to check your result with Checkpoint 6.
    # ----------

    


def RT_render_scene(scene, width, height, depth, buf):
    """Main function for rendering the scene
    Parameters
    ----------
    scene : bpy.types.Scene
        The scene that will be rendered
        It stores information about the camera, lights, objects, and material
    width : int
        Width of the rendered image
    height : int
        Height of the rendered image
    depth : int
        The recursion depth of raytracing
        i.e. the number that light bounces in the scene
    buf: numpy.ndarray
        the buffer that will be populated to store the calculated color
        for each pixel
    """

    # get all the lights from the scene
    scene_lights = [o for o in scene.objects if o.type == "LIGHT"]

    # get the location and orientation of the active camera
    cam_location = scene.camera.location
    cam_orientation = scene.camera.rotation_euler

    # get camera focal length
    focal_length = scene.camera.data.lens / scene.camera.data.sensor_width
    aspect_ratio = height / width

    # iterate through all the pixels, cast a ray for each pixel
    for y in range(height):
        # get screen space coordinate for y
        screen_y = ((y - (height / 2)) / height) * aspect_ratio
        for x in range(width):
            # get screen space coordinate for x
            screen_x = (x - (width / 2)) / width
            # calculate the ray direction
            ray_dir = Vector((screen_x, screen_y, -focal_length))
            ray_dir.rotate(cam_orientation)
            ray_dir = ray_dir.normalized()
            # populate the RGB component of the buffer with ray tracing result
            buf[y, x, 0:3] = RT_trace_ray(
                scene, cam_location, ray_dir, scene_lights, depth
            )
            # populate the alpha component of the buffer
            # to make the pixel not transparent
            buf[y, x, 3] = 1
        yield y
    return buf


# modified from https://docs.blender.org/api/current/bpy.types.RenderEngine.html
class SimpleRTRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "simple_RT"
    bl_label = "SimpleRT"
    bl_use_preview = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.draw_data = None

    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
    def __del__(self):
        pass

    # This is the method called by Blender for both final renders (F12) and
    # small preview for materials, world and lights.
    def render(self, depsgraph):
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        if self.is_preview:
            pass
        else:
            self.render_scene(scene)

    def render_scene(self, scene):
        # create a buffer to store the calculated intensities
        # buffer is has four channels: Red, Green, Blue, and Alpha
        # default is set to (0, 0, 0, 0), which means black and fully transparent
        height, width = self.size_y, self.size_x
        buf = np.zeros((height, width, 4))

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]

        # get the maximum ray tracing recursion depth
        depth = scene.simpleRT.recursion_depth

        # time the render
        import time
        from datetime import timedelta

        start_time = time.time()

        # start ray tracing
        update_cycle = int(10000 / width)
        for y in RT_render_scene(scene, width, height, depth, buf):

            # print render time info
            elapsed = int(time.time() - start_time)
            remain = int(elapsed / (y + 1) * (height - y - 1))
            print(
                f"rendering... Time {timedelta(seconds=elapsed)}"
                + f"| Remaining {timedelta(seconds=remain)}",
                end="\r",
            )

            # update Blender progress bar
            self.update_progress(y / height)

            # update render result
            # update too frequently will significantly slow down the rendering
            if y % update_cycle == 0 or y == height - 1:
                self.update_result(result)
                layer.rect = buf.reshape(-1, 4).tolist()

            # catch "ESC" event to cancel the render
            if self.test_break():
                break

        # tell Blender all pixels have been set and are final
        self.end_result(result)


def register():
    bpy.utils.register_class(SimpleRTRenderEngine)


def unregister():
    bpy.utils.unregister_class(SimpleRTRenderEngine)


if __name__ == "__main__":
    register()
