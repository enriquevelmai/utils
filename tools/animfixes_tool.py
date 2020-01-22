import maya.cmds as mc

window_name = 'AnimFixes'


def createUI():
    if mc.window(window_name, exists=True):
        mc.deleteUI(window_name)

    window = mc.window(window_name, title="LS Animation Fixes", w=330, h=450, rtf=True, mnb=False, mxb=False,
                       sizeable=False)

    # Creem una columna per a printar el missatge
    main_layout = mc.columnLayout(adjustableColumn=True, parent=window)
    image_layout = mc.columnLayout(adjustableColumn=False, parent=main_layout)
    mc.separator(h=15, style='none')
    mc.iconTextButton(image="C:/Users/enriq/Documents/animFixLogo.png", width=150, height=150, style='iconOnly',
                      parent=image_layout, useAlpha=True)

    tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5, parent=main_layout)

    # Cached
    tab1 = mc.columnLayout('CachedMain', adj=True, parent=tabs)
    mc.separator(h=15, style='none', parent=tab1)
    mc.text(label='Cached Geometry:', parent=tab1)
    mc.text(label='Select as many geos as you want', parent=tab1)
    mc.separator(h=15, style='none', parent=tab1)
    #
    cached_grid = mc.rowColumnLayout(adjustableColumn=True, numberOfColumns=2, columnAlign=(1, 'left'),
                                     columnSpacing=[5, 5],
                                     parent=tab1)
    mc.separator(h=5, style='none', parent=cached_grid)
    mc.separator(h=5, style='none', parent=cached_grid)
    mc.text(label='Number of tail frames:', parent=cached_grid)
    cached_number_of_frames_object = mc.intField(parent=cached_grid, value=2)
    mc.text(label='Press to start the corrective shape:', parent=cached_grid)
    mc.button(label='Active', parent=cached_grid,
              command=lambda x: create_corrective('Cached', cached_number_of_frames_object))
    mc.text(label='Press to finish the corrective shape:', parent=cached_grid)
    mc.button(label='Finish', parent=cached_grid, command=lambda x: clean_corrective('Cached'))
    mc.separator(h=15, style='none', parent=tab1)

    # Rigged
    tab2 = mc.columnLayout('RiggedMain', adj=True, parent=tabs)
    mc.separator(h=15, style='none', parent=tab2)
    mc.text(label='Rigged Geometry:', parent=tab2)
    mc.text(label='Select as many geos as you want', parent=tab2)
    mc.separator(h=15, style='none', parent=tab2)
    #
    rigged_grid = mc.rowColumnLayout(adjustableColumn=True, numberOfColumns=2, columnAlign=(1, 'left'),
                                     parent=tab2)
    mc.separator(h=5, style='none', parent=rigged_grid)
    mc.separator(h=5, style='none', parent=rigged_grid)
    mc.text(label='Number of tail frames:', parent=rigged_grid)
    rigged_number_of_frames_object = mc.intField(parent=rigged_grid, value=2)
    mc.text(label='Press to start the corrective shape:', parent=rigged_grid)
    mc.button(label='Active', parent=rigged_grid,
              command=lambda x: create_corrective('Rigged', rigged_number_of_frames_object))
    mc.text(label='Press to finish the corrective shape:', parent=rigged_grid)
    mc.button(label='Finish', parent=rigged_grid)
    mc.separator(h=15, style='none', parent=tab2)

    mc.tabLayout(tabs, edit=True, tabLabel=((tab1, 'Cached'), (tab2, 'Rigged')))
    mc.showWindow()


def create_corrective(type_form, frames):
    shapes_to_correct = mc.ls(sl=True)
    frames = mc.intField(frames, q=True, v=True)
    current_frame = int(mc.currentTime(q=True))
    correction_grp = 'correction_{}_c_grp'.format(str(current_frame).zfill(4))
    if not mc.objExists(correction_grp):
        correction_grp = mc.createNode('transform', name=correction_grp)

    if type_form == 'Cached':
        for shape in shapes_to_correct:
            corrected_shape = mc.duplicate(shape, name='{}_corrected_at_{}'.format(shape, str(current_frame).zfill(4)))[0]
            mc.parent(corrected_shape, correction_grp)
            mc.hide(shape)
            history_bls_node = [n for n in mc.listHistory(shape) if mc.objectType(n) == 'blendShape']
            if not history_bls_node:
                history_bls_node = [mc.blendShape(corrected_shape, shape, name='{}_corrected_BLS'.format(shape))]
            else:
                mc.blendShape(history_bls_node[0], e=True, target=[shape, 1, corrected_shape, 1])
            mc.select(history_bls_node[0])
            mc.setKeyframe(v=1, at=corrected_shape)
            mc.currentTime(current_frame - frames)
            mc.setKeyframe(v=0, at=corrected_shape)
            mc.currentTime(current_frame + frames)
            mc.setKeyframe(v=0, at=corrected_shape)
            mc.currentTime(current_frame)


def clean_corrective(type_form):
    current_frame = int(mc.currentTime(q=True))
    if type_form == 'Cached':
        correction_grp = 'correction_{}_c_grp'.format(str(current_frame).zfill(4))
        corrected_shapes = [mc.listRelatives(n, p=True)[0] for n in mc.listRelatives(correction_grp, ad=True, type='mesh')]
        for shape in corrected_shapes:
            mc.setAttr('{}.v'.format(shape.replace('_corrected_at_{}'.format(str(current_frame).zfill(4)), '')), 1)
        mc.delete('correction_{}_c_grp'.format(str(current_frame).zfill(4)))

createUI()