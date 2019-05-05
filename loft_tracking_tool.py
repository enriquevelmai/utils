import maya.cmds as mc

window_name = 'loft_tracking'


def create_ui():
    if mc.window(window_name, exists=True):
        mc.deleteUI(window_name)

    window = mc.window(window_name, title="(EV) Loft Tracking Creator", w=310, h=300, rtf=True, mnb=False, mxb=False,
                       sizeable=False)

    # Main Layout
    main_layout = mc.columnLayout(p=window, adjustableColumn=True)
    mc.separator(h=10, style='none')
    mc.text(label='1.- Select the first edge of a mesh, then load it.\n'
                  '2.- Select the second edge of a mesh, then load it.\n'
                  '3.- Set how much should the locator follow first or second edge.\n'
                  '4.- Press Go!\n'
                  '(all parameters can be changed after system creation)',
            parent=main_layout)
    mc.separator(h=10, style='in')

    # First Edge selection
    mc.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 80)],
                       columnSpacing=[(1, 0), (2, 10), (3, 10)],
                       columnAlign=(1, 'right'),
                       p=main_layout)
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.text(label='First Edge: ')
    first_edge_field = mc.textField()
    first_edge_select_button = mc.button(label='Load', command=lambda x: load_selection_to_texfield(first_edge_field))
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')

    # Second Edge Selection
    mc.text(label='Second Edge: ')
    second_edge_field = mc.textField()
    second_edge_select_button = mc.button(label='Load', command=lambda y: load_selection_to_texfield(second_edge_field))
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')

    # Amount settable
    mc.text(label='Amount: ')
    value_field = mc.floatField(value=0.5, maxValue=0.995, minValue=0.005)
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')
    mc.separator(h=5, style='none')

    # GO!
    mc.separator(h=15, style='in', parent=main_layout)
    go_button = mc.button('Go!',
                          command=lambda z: execute_loft_tracking(first_edge_field, second_edge_field, value_field),
                          parent=main_layout)
    mc.separator(h=15, style='none', parent=main_layout)

    mc.showWindow(window)


def load_selection_to_texfield(object):
    selection = str(mc.ls(sl=True)[0])
    mc.textField(object, e=True, text=selection)


def execute_loft_tracking(first_edge_field, second_edge_field, value_field):
    # get data from ui
    first_edge_raw = mc.textField(first_edge_field, q=True, text=True)
    second_edge_raw = mc.textField(second_edge_field, q=True, text=True)
    value = float(mc.floatField(value_field, q=True, value=True))

    # get data as needed
    first_mesh = str(first_edge_raw.split('.')[0])
    first_edge_number = int(first_edge_raw.split('[')[1].split(']')[0])
    #
    second_mesh = str(second_edge_raw.split('.')[0])
    second_edge_number = int(second_edge_raw.split('[')[1].split(']')[0])

    # create main node, it works as a settings one
    main_trn = mc.createNode('transform',
                             name='{}_{}_to_{}_{}_TRN'.format(first_mesh,
                                                              first_edge_number,
                                                              second_mesh,
                                                              second_edge_number)
                             )
    for trn in 'trs':
        for axis in 'xyz':
            mc.setAttr('{}.{}{}'.format(main_trn, trn, axis), lock=True, keyable=False, channelBox=False)
    mc.setAttr('{}.v'.format(main_trn), lock=True, keyable=False, channelBox=False)
    mc.addAttr(main_trn, attributeType='long', longName='firstEdge', defaultValue=first_edge_number, keyable=False)
    mc.addAttr(main_trn, attributeType='long', longName='secondEdge', defaultValue=second_edge_number, keyable=False)
    mc.addAttr(main_trn, attributeType='float', longName='parameter', defaultValue=value, minValue=0.005,
               maxValue=0.995, keyable=True)
    mc.setAttr('{}.firstEdge'.format(main_trn), e=True, channelBox=True)
    mc.setAttr('{}.secondEdge'.format(main_trn), e=True, channelBox=True)

    # create logic
    cme1 = mc.createNode('curveFromMeshEdge', name='{}_{}_CME'.format(first_mesh, first_edge_number))
    cme2 = mc.createNode('curveFromMeshEdge', name='{}_{}_CME'.format(second_mesh, second_edge_number))
    out_nrb_shape = mc.createNode('nurbsSurface', name='{}_{}_to_{}_{}_NRBShape'.format(first_mesh,
                                                                                        first_edge_number,
                                                                                        second_mesh,
                                                                                        second_edge_number)
                                  )
    out_nrb_trn = mc.rename(mc.listRelatives(out_nrb_shape, p=True)[0], '{}_{}_to_{}_{}_NRB'.format(first_mesh,
                                                                                                    first_edge_number,
                                                                                                    second_mesh,
                                                                                                    second_edge_number))
    loft = mc.createNode('loft', name='{}_{}_to_{}_{}_LFT'.format(first_mesh,
                                                                  first_edge_number,
                                                                  second_mesh,
                                                                  second_edge_number)
                         )
    #
    mc.parent(out_nrb_trn, main_trn)
    mc.connectAttr('{}.worldMesh[0]'.format(first_mesh), '{}.inputMesh'.format(cme1))
    mc.connectAttr('{}.firstEdge'.format(main_trn), '{}.edgeIndex[0]'.format(cme1))
    mc.connectAttr('{}.worldMesh[0]'.format(second_mesh), '{}.inputMesh'.format(cme2))
    mc.connectAttr('{}.secondEdge'.format(main_trn), '{}.edgeIndex[0]'.format(cme2))
    mc.connectAttr('{}.outputCurve'.format(cme1), '{}.inputCurve[0]'.format(loft))
    mc.connectAttr('{}.outputCurve'.format(cme2), '{}.inputCurve[1]'.format(loft))
    mc.connectAttr('{}.outputSurface'.format(loft), '{}.create'.format(out_nrb_shape))
    # rebuild out surface to normalize the uv coord
    mc.rebuildSurface(out_nrb_trn,
                      constructionHistory=1,
                      replaceOriginal=1,
                      rebuildType=0,
                      endKnots=1,
                      keepRange=0,
                      keepControlPoints=0,
                      keepCorners=0,
                      spansU=1,
                      degreeU=1,
                      spansV=1,
                      degreeV=1,
                      tolerance=0.0001,
                      fitRebuild=0,
                      direction=2,
                      name='{}_rebuild'.format(out_nrb_trn))

    # create out locator
    msa = mc.createNode('cMuscleSurfAttach', name='{}_{}_to_{}_{}_MSAShape'.format(first_mesh,
                                                                                   first_edge_number,
                                                                                   second_mesh,
                                                                                   second_edge_number))
    msa_trn = mc.rename(mc.listRelatives(msa, parent=True)[0], '{}_{}_to_{}_{}_MSA'.format(first_mesh,
                                                                                           first_edge_number,
                                                                                           second_mesh,
                                                                                           second_edge_number))
    mc.parent(msa_trn, main_trn)
    mc.connectAttr('{}.outRotate'.format(msa), '{}.r'.format(msa_trn))
    mc.connectAttr('{}.outTranslate'.format(msa), '{}.t'.format(msa_trn))

    mc.connectAttr('{}.worldSpace[0]'.format(out_nrb_shape), '{}.surfIn'.format(msa))
    mc.connectAttr('{}.parameter'.format(main_trn), '{}.uLoc'.format(msa))
    mc.setAttr('{}.vLoc'.format(msa), 0.5)


create_ui()
