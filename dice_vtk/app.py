# Standard Python modules
# =======================
import json
import itertools
import os

# External modules
# ================

# DICE modules
# ============
from dice_tools import diceSlot, diceProperty, instantiate, wizard
from dice_tools.helpers.xmodel import list_of_dicts_model
from dice_vtk import VtkScene


class VisApp:
    """
    Base class for DICE applications to use VTK. It implements predefined
    interactive 3D VTK scenes with UI controls for geometry object
    manipulations in scenes. Scenes could be dynamically added and removed.
    Scenes characteristics are saved to 'vis.json' in application`s config_dir
    and loaded back on next application start.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debug("Starting VisApp")
        self.__scenes_model = list_of_dicts_model('sceneName', 'scene')
        self.__save_cfg_pending = False
        wizard.subscribe(self, self.__scenes_model)
        wizard.subscribe(self, self.__scenes_model.data)
        wizard.subscribe('w_idle', self.__save_config)

        self.__scenes = {}
        self.__prepare_config()
        if not self.__scenes:
            self.vis_add_scene('Scene_1', 'default')
        current_index = self.__config.get('current', 0)
        self.vis_activate_scene(current_index)

    def vis_scenes_by_tag(self, tag):
        return [v for v in self.__scenes.values() if v.tag == tag]

    @diceSlot('int', name='visActivateScene')
    def vis_activate_scene(self, index):
        for i, v in enumerate(self.__scenes_model.root_item.elements):
            if i == index:
                v['scene'].active = True
                self.__scenes_model.current_item = v
            else:
                v['scene'].active = False
        self.__config['current'] = index
        self.__save_cfg_pending = True

    def w_model_current_changed(self, model, current, prev):
        for i, v in enumerate(self.__scenes_model.root_item.elements):
            if v == current:
                self.__config['current'] = i
                self.__save_cfg_pending = True

    def w_item_updated(self, model_data, item, key, value, old_value):
        if key == 'sceneName':
            self.__scenes[value] = self.__scenes[old_value]
            del self.__scenes[old_value]
            for v in self.__config['scenes']:
                if v['name'] == old_value:
                    v['name'] = value
                    break
            self.__save_cfg_pending = True

    @diceSlot(int, int, name='visMoveScene')
    def vis_move_scene(self, pos, to):
        """
        Moves scene in model from pos to to.
        :param pos: Current scene position.
        :param to: New scene position.
        """
        if pos == to:
            return
        if to > pos:
            to += 1
        root = self.__scenes_model.root_item
        self.__scenes_model.data.move(root, pos, 1, root, to)
        item = self.__config['scenes'].pop(pos)
        self.__config['scenes'].insert(to, item)
        self.__config['current'] = to
        self.__save_cfg_pending = True

    def __prepare_config(self):
        path = self.config_path("vis.json")
        if os.path.exists(path):
            with open(path) as f:
                self.__config = json.load(f)
        else:
            self.__config = {}

        for v in self.__config.setdefault('scenes', []):
            name = v['name']
            tag = v['tag']
            self.vis_add_scene(name, tag, save=False, activate=False)
            if 'camera' in v:
                self.__scenes[name].set_camera_params(**v['camera'])

    def __save_config(self):
        if self.__save_cfg_pending:
            self.__save_cfg_pending = False
            with open(self.config_path('vis.json'), 'w') as f:
                json.dump(self.__config, f)

    def w_scene_camera_updated(self, scene, **kwargs):
        for k, v in self.__scenes.items():
            if v == scene:
                for s in self.__config['scenes']:
                    if s['name'] == k:
                        s['camera'] = kwargs
                        self.__save_cfg_pending = True

    @diceProperty('QVariant', name="visModel")
    def vis_model(self):
        """
        Model with application scenes.
        """
        return self.__scenes_model

    @diceSlot(int, name='visDeleteScene')
    def vis_delete_scene(self, index):
        """
        Removes scene from application.
        :param index: Scene number.
        """
        name = self.__scenes_model.root_item.elements[index]['sceneName']
        del self.__config['scenes'][index]
        if self.__config['current'] == index:
            self.vis_activate_scene(index - 1)
        else:
            if self.__config['current'] > index:
                self.__config['current'] -= 1
            self.__save_cfg_pending = True

        del self.__scenes_model.root_item.elements[index]
        self.__scenes[name].delete()
        del self.__scenes[name]

    @diceSlot(name="visAddScene")
    @diceSlot("QString", name="visAddScene")
    def vis_add_scene(self, scene_name="Scene_1", tag='default', save=True, activate=True):
        """
        Adds scene to application.
        :param scene_name: Name of scene to add. Defaults to "Scene_1".
        """

        self.debug("Adding scene " + str(scene_name))

        if scene_name in self.__scenes:
            for i in itertools.count(1):
                new_name = scene_name.split('_')[0] + "_" + str(i)
                if new_name not in self.__scenes:
                    scene_name = new_name
                    break

        scene = VtkScene(200, 200)
        scene.tag = tag
        scene.scene_name = scene_name
        if save:
            new_scene_config = {'name': scene_name, 'tag': tag}
            self.__config['scenes'].append(new_scene_config)
            self.__save_cfg_pending = True

        for v in self.vis_scenes_by_tag(tag):
            for o in v.objects:
                scene.add_object(o)
            break

        wizard.subscribe(self, scene)
        self.__scenes[scene_name] = scene
        item = dict(sceneName=scene_name, scene=scene)
        idx = len(self.__scenes_model.root_item.elements)
        self.__scenes_model.root_item.elements.append(item)
        if activate:
            self.vis_activate_scene(idx)

    def vis_add_object(self, obj, tag='default', reset_camera=True):
        """
        Adds geometry object to all scenes in application.
        :param obj: Geometry object. A GeometryBase inheritor.
        """
        for v in self.__scenes.values():
            if v.tag == tag:
                v.add_object(obj, reset_camera)

    def vis_remove_object(self, obj):
        """
        Removes geometry object from all scenes in application.
        :param obj: Geometry object. A GeometryBase inheritor.
        """
        for v in self.__scenes.values():
            v.remove_object(obj)

    def vis_clear(self, tag = 'default'):
        """
        Removes all geometry object from all scenes in application.
        """
        for v in self.__scenes.values():
            if v.tag == tag:
                v.clear()

    def vis_get_scene(self, scene_name):
        """
        Gets scene object by it`s name.
        :param scene_name: Name of application scene.
        :return: VtkScene object.
        """
        if scene_name in self.__scenes:
            return self.__scenes[scene_name]

    def vis_reset_camera(self, tag = 'default'):
        """
        Removes all geometry object from all scenes in application.
        """
        for v in self.__scenes.values():
            if v.tag == tag:
                v.reset_camera()

