# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

"""textureTypes = {
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
    }"""

def createCyclesMaterial(material, textures):
    group = bpy.data.node_groups.new(name=material.name, type="ShaderNodeTree")

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
    node_output.inputs[2].default_value = 0.5
    
    group.inputs.new(name="Vector", type="NodeSocketVector")

    if len(textures) == 0:
        return

    yOffset = 0

    for texture in textures:
        node_texture = group_nodes.new(type="ShaderNodeTexImage")
        node_texture.location = -400, yOffset
        
        image = bpy.data.images.get(texture[0])
        node_texture.image = image
        
        group_links.new(node_input.outputs[0], node_texture.inputs[0])

        if texture[1] == "TS_COLOR_MAP":
            group_links.new(node_texture.outputs[0], node_output.inputs[0])
            group_links.new(node_texture.outputs[1], node_output.inputs[3])

            
        elif texture[1] == "TS_NORMAL_MAP":
            node_texture.color_space = "NONE"

            group_links.new(node_texture.outputs[0], node_output.inputs[2])
            
        elif texture[1] == "TS_SPECULAR_MAP":
            node_texture.color_space = "NONE"

            group_links.new(node_texture.outputs[0], node_output.inputs[1])
            
        else:
            print("unknown texture " + str(textures[0]) + " type: " + texture[1])

        yOffset -= 260

    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in nodes:
        nodes.remove(node)

    node_uvmap = nodes.new(type="ShaderNodeUVMap")
    node_uvmap.location = -800, 0
    node_uvmap.uv_map = "UVMap"

    node_textures = nodes.new(type="ShaderNodeGroup")
    node_textures.location = -600, 0
    node_textures.node_tree = group

    links.new(node_uvmap.outputs[0], node_textures.inputs[0])

    node_invert = nodes.new(type="ShaderNodeInvert")
    node_invert.location = -400, -400

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
    links.new(node_textures.outputs[1], node_invert.inputs[1])
    links.new(node_invert.outputs[0], node_mult_2.inputs[0])
    links.new(node_textures.outputs[2], node_bump.inputs[2])
    
    links.new(node_bump.outputs[0], node_shader.inputs["Normal"])
    links.new(node_mult_1.outputs[0], node_shader.inputs["Specular"])
    links.new(node_mult_2.outputs[0], node_shader.inputs["Roughness"])

    node_transparent = nodes.new(type="ShaderNodeBsdfTransparent")
    node_transparent.location = 0, -500

    node_mix = nodes.new(type="ShaderNodeMixShader")
    node_mix.location = 200, 0

    links.new(node_textures.outputs[3], node_mix.inputs[0])
    links.new(node_shader.outputs[0], node_mix.inputs[2])
    links.new(node_transparent.outputs[0], node_mix.inputs[1])

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = 400, 0

    links.new(node_mix.outputs[0], node_output.inputs[0])

