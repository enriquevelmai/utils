import maya.cmds as mc


def orient_joints_as_parent():
    for first_joint in mc.ls(sl=True):
        other_joints = mc.listRelatives(first_joint, ad=True)
        other_joints.reverse()

        for i, jnt in enumerate(other_joints):
            if i + 1 != len(other_joints):
                mc.parent(other_joints[i + 1], w=True)
                mc.setAttr('{}.jointOrientX'.format(jnt), 0)
                mc.parent(other_joints[i + 1], jnt)
            else:
                mc.setAttr('{}.jointOrient'.format(jnt), 0, 0, 0)


def joint_from_matrix(matrix, name='joint', side='C'):
    joint = mc.createNode('joint', n='{}_{}_JNT'.format(side, name))
    mc.xform(joint, m=matrix, ws=True)
    mc.makeIdentity(joint, apply=True, r=True, n=0, pn=True)
    return joint


def joints_from_matrix_list(matrix_list, name='joint', side='C'):
    if len(matrix_list) == 1:
        joint = joint_from_matrix(matrix=matrix_list[0], name=name, side=side)
        return [joint]
    else:
        joint_list = list()
        for i, matrix in enumerate(matrix_list):
            joint = joint_from_matrix(matrix=matrix, name=name + str(i).zfill(2), side=side)
            joint_list.append(joint)
            if i == 0:
                continue
            mc.parent(joint, joint_list[i - 1])

        mc.joint(joint_list[0], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        for axis in "XYZ":
            mc.setAttr('{}.jointOrient{}'.format(joint_list[-1], axis), 0)

        return joint_list


def label_joints():
    """
    This method labels joints regarding with its name
    side as the split of '_' as first return name as second
    """
    side_dict = {'C': 0,
                 'L': 1,
                 'R': 2}
    for jnt in mc.ls(type='joint'):
        mc.setAttr('{}.side'.format(jnt), side_dict[jnt.split('_')[0]])
        mc.setAttr('{}.type'.format(jnt), 18)
        mc.setAttr('{}.otherType'.format(jnt), jnt.split('_')[1], type="string")


def duplicate_hierarchy(joint_list, name, side):
    new_joint_list = list()
    for i, jnt in enumerate(joint_list):
        new_joint = joint_from_matrix(matrix=mc.xform(jnt, q=True, m=True, ws=True),
                                      name='{}{}'.format(name, str(i).zfill(2)), side=side)
        if i != 0:
            mc.parent(new_joint, new_joint_list[i - 1])
        new_joint_list.append(new_joint)
    return new_joint_list


def orient_plane():
    raise NotImplementedError


def sliding_joints():
    raise NotImplementedError
