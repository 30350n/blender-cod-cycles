import bpy, os

textureTypes = {
    0  : "TS_2D",
    1  : "TS_FUNCTION",
    2  : "TS_COLOR_MAP",
    3  : "TS_UNUSED_1",
    4  : "TS_UNUSED_2",
    5  : "TS_NORMAL_MAP",
    6  : "TS_UNUSED_3",
    7  : "TS_UNUSED_4",
    8  : "TS_SPECULAR_MAP",
    9  : "TS_UNUSED_5",
    10 : "TS_UNUSED_6",
    11 : "TS_WATER_MAP",
    }

def createMaterial(name, textures):
    group = bpy.data.node_groups.new(name=name, type="ShaderNodeTree")

    group_nodes = group.nodes
    group_links = group.links

    node_output = group_nodes.new(type="NodeGroupOutput")
    node_output.location = 0, 0
    
    node_input = group_nodes.new(type="NodeGroupInput")
    node_input.location = -600, 0
    
    group.outputs.new(name="Diffuse", type="NodeSocketColor")
    group.outputs.new(name="Specular", type="NodeSocketFloat")
    group.outputs.new(name="Normal", type="NodeSocketFloat")
    group.outputs.new(name="Alpha", type="NodeSocketFloat")
    
    node_output.inputs[1].default_value = 0.5
    
    group.inputs.new(name="Vector", type="NodeSocketVector")

    if len(textures) == 0:
        return

    yOffset = 0

    lastColorMap = None

    for texture in textures:
        node_texture = group_nodes.new(type="ShaderNodeTexImage")
        node_texture.location = -400, yOffset
        
        image = bpy.data.images.get(texture[0] + ".dds")
        node_texture.image = image
        
        group_links.new(node_input.outputs[0], node_texture.inputs[0])

        if textureTypes[texture[1]] == "TS_COLOR_MAP":
            node_multiply = group_nodes.new(type="ShaderNodeMath")
            node_multiply.operation = "MULTIPLY"
            node_multiply.location = -200, yOffset
            
            if lastColorMap == None:
                group_links.new(node_texture.outputs[0], node_output.inputs[0])
                group_links.new(node_texture.outputs[1], node_multiply.inputs[0])
                group_links.new(node_multiply.outputs[0], node_output.inputs[3])

            else:
                node_mix = group_nodes.new(type="ShaderNodeMixRGB")
                node_mix.location = 0, yOffset

                group_links.new(lastColorMap[0].outputs[0], node_mix.inputs[0])
                group_links.new(node_texture.outputs[0], node_mix.inputs[1])
                group_links.new(node_mix.outputs[0], node_output.inputs[0])
                
                group_links.new(lastColorMap[1].outputs[0], node_multiply.inputs[0])
                group_links.new(node_texture.outputs[1], lastColorMap[1].inputs[1])
                group_links.new(node_multiply.outputs[0], node_output.inputs[3])

            lastColorMap = [node_texture, node_multiply]
            
        elif textureTypes[texture[1]] == "TS_NORMAL_MAP":
            node_texture.color_space = "NONE"

            group_links.new(node_texture.outputs[0], node_output.inputs[2])
            
        elif textureTypes[texture[1]] == "TS_SPECULAR_MAP":
            node_texture.color_space = "NONE"

            group_links.new(node_texture.outputs[0], node_output.inputs[1])
            
        else:
            print("unknown texture " + str(textures[0]) + " type: " + textureTypes[texture[1]])

        yOffset -= 260

    material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in nodes:
        nodes.remove(node)

    node_uvmap = nodes.new(type="ShaderNodeUVMap")
    node_uvmap.location = -600, yOffset
    node_uvmap.uv_map = "UVMap"

    node_textures = nodes.new(type="ShaderNodeGroup")
    node_textures.location = -400, 0
    node_textures.node_tree = group

    links.new(node_uvmap.outputs[0], node_textures.inputs[0])

    node_bump = nodes.new(type="ShaderNodeBump")
    node_bump.location = -200, 0
    node_bump.inputs[0].default_value = 0.5

    node_mult_1 = nodes.new(type="ShaderNodeMath")
    node_mult_1.location = -200, -200
    node_mult_1.operation = "MULTIPLY"
    node_mult_1.inputs[1].default_value = 1

    node_mult_2 = nodes.new(type="ShaderNodeMath")
    node_mult_2.location = -200, -400
    node_mult_2.operation = "MULTIPLY"
    node_mult_2.inputs[1].default_value = 1
    
    node_shader = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_shader.location = 0, 0

    links.new(node_textures.outputs[0], node_shader.inputs["Base Color"])
    links.new(node_textures.outputs[1], node_mult_1.inputs[0])
    links.new(node_textures.outputs[1], node_mult_2.inputs[0])
    links.new(node_textures.outputs[2], node_bump.inputs[2])
    
    links.new(node_bump.outputs[0], node_shader.inputs["Normal"])
    links.new(node_mult_1.outputs[0], node_shader.inputs["Specular"])
    links.new(node_mult_2.outputs[0], node_shader.inputs["Roughness"])

    node_transparent = nodes.new(type="ShaderNodeBsdfTransparent")
    node_transparent.location = 0, -600

    node_mix = nodes.new(type="ShaderNodeMixShader")
    node_mix.location = 200, 0

    links.new(node_textures.outputs[3], node_mix.inputs[0])
    links.new(node_shader.outputs[0], node_mix.inputs[2])
    links.new(node_transparent.outputs[0], node_mix.inputs[1])

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = 400, 0

    links.new(node_mix.outputs[0], node_output.inputs[0])
    
    return material
