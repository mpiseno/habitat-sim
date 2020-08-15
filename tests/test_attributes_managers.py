#!/usr/bin/env python3

import magnum as mn

import examples.settings


def perform_general_tests(attr_mgr, search_string):
    # get size of template library
    orig_num_templates = attr_mgr.get_num_templates()
    # make sure this is same value as size of template handles list
    assert orig_num_templates > 0

    # search for attributes with expected string
    template_handles = attr_mgr.get_template_handles(search_string)
    # verify handle exists
    assert len(template_handles) > 0

    template_handle = template_handles[0]
    # get id from handle
    template_ID = attr_mgr.get_template_ID_by_handle(template_handle)
    assert search_string in template_handle

    # verify that access is the same for ID and handle lookup
    template0 = attr_mgr.get_template_by_handle(template_handle)
    template1 = attr_mgr.get_template_by_ID(template_ID)

    # verify template 0 and template 1 are copies of the same template
    assert template0.handle == template1.handle
    assert template0.ID == template1.ID

    # modify template, register, then verify that
    # retrieved template is not same as previous template
    template0.set("test_key", "template0_test")
    template1.set("test_key", "template1_test")

    # save modified template
    attr_mgr.register_template(template0, template_handle)
    # retrieve registered template
    template2 = attr_mgr.get_template_by_handle(template_handle)

    # verify templates have the same identifiers
    assert template1.handle == template2.handle
    assert template1.ID == template2.ID

    # verify the templates hold different data and are not the
    # same object
    assert template1.get_string("test_key") != template2.get_string("test_key")
    # verify 0 and 2 hold same user-set value
    assert template0.get_string("test_key") == template2.get_string("test_key")

    # change retrieved template, verify it is not same object as template0
    template2.set("test_key", "template2_test")

    # verify the templates hold different data and are not the
    # same object
    assert template0.get_string("test_key") != template2.get_string("test_key")

    # add new template
    attr_mgr.register_template(template0, "new_template_0")

    # register new template and verify size is greater than original
    curr_num_templates = attr_mgr.get_num_templates()
    assert curr_num_templates != orig_num_templates

    # get template that is removed
    template3 = attr_mgr.remove_template_by_handle("new_template_0")

    # verify not NONE
    assert template3 != None
    # verify has expected handle
    assert template3.handle == "new_template_0"

    # get new size of library after remove and verify same as original
    curr_num_templates = attr_mgr.get_num_templates()
    assert curr_num_templates == orig_num_templates

    return template0, template3


def perform_add_blank_template_test(attr_mgr, valid_render_handle=None):
    # get size of template library
    orig_num_templates = attr_mgr.get_num_templates()

    # add new blank template
    new_template_handle = "new template"

    # create new default template, do not register it
    new_template0 = attr_mgr.create_new_template(new_template_handle, False)

    # change new template field
    new_template0.set("test_key", "new_template_test")

    # give new template valid render asset handle, otherwise registration might fail
    if valid_render_handle is not None:
        new_template0.render_asset_handle = valid_render_handle

    # add new template
    attr_mgr.register_template(new_template0, new_template_handle)

    # get new size of library after remove and verify not same as original
    curr_num_templates = attr_mgr.get_num_templates()
    assert curr_num_templates > orig_num_templates

    # verify new template added properly
    new_template1 = attr_mgr.get_template_by_handle(new_template_handle)

    # verify template 0 and template 1 are copies of the same template
    assert new_template0.handle == new_template1.handle
    assert new_template0.ID == new_template1.ID
    assert new_template0.get_string("test_key") == new_template1.get_string("test_key")

    # remove newly added default template
    new_template2 = attr_mgr.remove_template_by_handle(new_template_handle)

    # verify added template was one removed
    assert new_template0.handle == new_template2.handle
    assert new_template0.ID == new_template2.ID
    assert new_template0.get_string("test_key") == new_template2.get_string("test_key")

    # get new size of library after remove and verify same as original
    curr_num_templates = attr_mgr.get_num_templates()
    assert curr_num_templates == orig_num_templates


def test_physics_attributes_managers(sim):
    cfg_settings = examples.settings.default_sim_settings.copy()
    cfg_settings["scene"] = "data/scene_datasets/habitat-test-scenes/van-gogh-room.glb"
    cfg_settings["enable_physics"] = True
    hab_cfg = examples.settings.make_cfg(cfg_settings)
    sim.reconfigure(hab_cfg)

    # get attribute managers
    phys_attr_mgr = sim.get_physics_template_manager()

    # perform general tests for this attributes manager
    template0, _ = perform_general_tests(
        phys_attr_mgr, cfg_settings["physics_config_file"]
    )

    # verify that physics template matches expected values in file
    assert template0.timestep == 0.008
    assert template0.simulator == "bullet"

    # verify creating new template
    perform_add_blank_template_test(phys_attr_mgr)


def test_scene_attributes_managers(sim):
    cfg_settings = examples.settings.default_sim_settings.copy()
    cfg_settings["scene"] = "data/scene_datasets/habitat-test-scenes/van-gogh-room.glb"
    cfg_settings["enable_physics"] = True
    hab_cfg = examples.settings.make_cfg(cfg_settings)
    sim.reconfigure(hab_cfg)

    scene_name = cfg_settings["scene"]

    # get attribute managers
    scene_mgr = sim.get_scene_template_manager()

    # perform general tests for this attributes manager
    template0, _ = perform_general_tests(scene_mgr, scene_name)

    # verify gravity in template is as expected
    assert template0.gravity == mn.Vector3(0.0, -9.8, 0.0)

    # verify creating new template
    perform_add_blank_template_test(scene_mgr, template0.render_asset_handle)


def test_object_attributes_managers(sim):
    cfg_settings = examples.settings.default_sim_settings.copy()
    cfg_settings["scene"] = "data/scene_datasets/habitat-test-scenes/van-gogh-room.glb"
    cfg_settings["enable_physics"] = True
    hab_cfg = examples.settings.make_cfg(cfg_settings)
    sim.reconfigure(hab_cfg)

    # get object attribute managers
    obj_mgr = sim.get_object_template_manager()

    # get object template random handle
    rand_obj_handle = obj_mgr.get_random_template_handle()

    # perform general tests for object attribute manager
    template0, _ = perform_general_tests(obj_mgr, rand_obj_handle)

    # verify creating new template
    perform_add_blank_template_test(obj_mgr, template0.render_asset_handle)


def perform_asset_attrib_mgr_tests(
    attr_mgr, default_attribs, ctor_mod_field, legalVal, illegalVal
):
    # get size of template library
    orig_num_templates = attr_mgr.get_num_templates()
    # make sure this is same value as size of template handles list
    assert orig_num_templates > 0

    # get old handle - based on how default_attribs was constructed
    old_handle = default_attribs.handle

    # verify that default_attribs is valid
    assert default_attribs.is_valid_template

    # modify field values that impact primitive construction, if exist
    if "none" != ctor_mod_field:
        default_attribs.set(ctor_mod_field, illegalVal)
        # verify that this is now an illegal template
        assert not (default_attribs.is_valid_template)

    # modify to hold legal value
    default_attribs.set(ctor_mod_field, legalVal)

    # verify that default_attribs is valid
    assert default_attribs.is_valid_template

    # build new handle reflected in modified template.
    # This is only necessary because we are bypassing setters
    default_attribs.build_handle()

    # verify that new handle is different from old handle
    new_handle = default_attribs.handle
    assert new_handle != old_handle

    # register new template
    attr_mgr.register_template(default_attribs)

    # verify that both templates now exist in library
    assert attr_mgr.get_library_has_handle(new_handle)
    assert attr_mgr.get_library_has_handle(old_handle)

    # get new and old templates
    old_template = attr_mgr.get_template_by_handle(old_handle)
    new_template = attr_mgr.get_template_by_handle(new_handle)

    # verify they do not hold the same values in the important fields
    assert old_template.get_int(ctor_mod_field) != new_template.get_int(ctor_mod_field)
    # verify we have more templates than when we started
    assert orig_num_templates != attr_mgr.get_num_templates()

    # delete new template
    deleted_template = attr_mgr.remove_template_by_handle(new_handle)
    assert deleted_template != None

    # verify we are back where we started
    assert orig_num_templates == attr_mgr.get_num_templates()


def test_asset_attributes_managers(sim):
    cfg_settings = examples.settings.default_sim_settings.copy()
    cfg_settings["scene"] = "data/scene_datasets/habitat-test-scenes/van-gogh-room.glb"
    cfg_settings["enable_physics"] = True
    hab_cfg = examples.settings.make_cfg(cfg_settings)
    sim.reconfigure(hab_cfg)

    # legal and illegal vals for primitives based on wireframe or solid
    legal_mod_val_wf = 64
    illegal_mod_val_wf = 25
    legal_mod_val_solid = 5
    illegal_mod_val_solid = 0

    # get object attribute managers
    attr_mgr = sim.get_asset_template_manager()

    # capsule
    print("Test Capsule attributes construction, modification, saving and removal.")
    dflt_solid_attribs = attr_mgr.get_default_capsule_template(False)
    perform_asset_attrib_mgr_tests(
        attr_mgr,
        dflt_solid_attribs,
        "segments",
        legal_mod_val_solid,
        illegal_mod_val_solid,
    )
    dflt_wf_attribs = attr_mgr.get_default_capsule_template(True)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_wf_attribs, "segments", legal_mod_val_wf, illegal_mod_val_wf
    )

    # cone
    print("Test Cone attributes construction, modification, saving and removal.")
    dflt_solid_attribs = attr_mgr.get_default_cone_template(False)
    perform_asset_attrib_mgr_tests(
        attr_mgr,
        dflt_solid_attribs,
        "segments",
        legal_mod_val_solid,
        illegal_mod_val_solid,
    )
    dflt_wf_attribs = attr_mgr.get_default_cone_template(True)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_wf_attribs, "segments", legal_mod_val_wf, illegal_mod_val_wf
    )

    # cylinder
    print("Test Cylinder attributes construction, modification, saving and removal.")
    dflt_solid_attribs = attr_mgr.get_default_cylinder_template(False)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_solid_attribs, "segments", 5, illegal_mod_val_solid
    )
    dflt_wf_attribs = attr_mgr.get_default_cylinder_template(True)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_wf_attribs, "segments", legal_mod_val_wf, illegal_mod_val_wf
    )

    # UVSphere
    print("Test UVSphere attributes construction, modification, saving and removal.")
    dflt_solid_attribs = attr_mgr.get_default_UVsphere_template(False)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_solid_attribs, "segments", 5, illegal_mod_val_solid
    )
    dflt_wf_attribs = attr_mgr.get_default_UVsphere_template(True)
    perform_asset_attrib_mgr_tests(
        attr_mgr, dflt_wf_attribs, "segments", legal_mod_val_wf, illegal_mod_val_wf
    )
