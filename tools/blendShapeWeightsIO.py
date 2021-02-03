import json
import os
import maya.cmds as mc

home_dir = os.environ["HOME"]

# create weights dir
weights_dir = os.path.join(home_dir, "weights")
if not os.path.exists(weights_dir):
    os.makedirs(weights_dir)


def get_current_version(tag):
    # get new version weights
    xml_files = [f for f in os.listdir(weights_dir) if f.endswith(".xml") and tag in f]
    if not xml_files:
        return 0
    xml_files.sort()
    last_file = xml_files[-1]

    last_file_name = last_file.split(".")[0]
    version = int(last_file_name.split("_")[-1])
    return version


# export weights
def export_weights():
    for bls_node in mc.ls(type="blendShape"):
        version = get_current_version(tag=bls_node) + 1

        xml_file = "{}_{}.xml".format(bls_node, str(version).zfill(3))
        json_file = "{}_{}.json".format(bls_node, str(version).zfill(3))

        # default maya export
        mc.deformerWeights(
            xml_file,
            path=weights_dir,
            format="XML",
            export=True,
            deformer=bls_node)

        # fix of base weights export
        base_weights = dict()
        list_to_fill = list()
        base_geo = mc.deformer(bls_node, g=True, q=True)
        for i, vtx in enumerate(mc.ls("{}.vtx[*]".format(base_geo), fl=True)):
            list_to_fill.append(mc.getAttr("{}.it[0].bw[{}]".format(bls_node, i)))
        base_weights["base_weights"] = [list_to_fill]
        with open(os.path.join(weights_dir, json_file), "w+") as f:
            json.dump(base_weights, f)


# import
def import_weights():
    for bls_node in mc.ls(type="blendShape"):
        version = get_current_version(tag=bls_node)
        if not version:
            return

        xml_file = "{}_{}.xml".format(bls_node, str(version).zfill(3))
        json_file = "{}_{}.json".format(bls_node, str(version).zfill(3))

        # default maya import
        mc.deformerWeights(xml_file,
                           path=weights_dir,
                           format="XML",
                           im=True,
                           deformer=bls_node)

        # fix of import base weights
        with open(os.path.join(weights_dir, json_file), "r") as f:
            base_weights = json.load(f)
        for i, value in enumerate(*base_weights["base_weights"]):
            mc.setAttr("{}.it[0].bw[{}]".format(bls_node, i), value)


# export_weights()
import_weights()
