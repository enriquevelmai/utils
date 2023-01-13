import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx


class MiniCommand(ommpx.MPxCommand):
    COMMAND_NAME = "miniCommand"
    VENDOR = 'Kike'
    VERSION = '1.0'

    EXAMPLE_FLAGS = ["-ex", "-example"]

    def __init__(self):
        ommpx.MPxCommand.__init__(self)

    def doIt(self, arg_list):
        """
        Method that is called when the command is executed
        :param arg_list: (list): containing all the arguments given in the command call
        """
        # create a database with the input arguments
        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.displayError("Error parsing arguments")
            raise

        # then use the arg_db.isFlagSet(MiniCommand.EXAMPLE_FLAGS[0]) to query if the user have given this specific flag
        # then use the arg_db.flagArgumentString(MiniCommand.EXAMPLE_FLAGS[0], 0) to query the value of the flag
        # then use the arg_db.flagArgumentString(MiniCommand.EXAMPLE_FLAGS[0], 1) the value of the flag second argument

        # then use the arg_db.commandArgumentString(0) to query the positional arguments of the command, notice you will
        # have to add a proper exception message if the user does not provide any positional argument

        # in order to have get the selection list arguments you could use the function
        sel_list = om.MSelectionList()
        arg_db.getObjects(sel_list)

        # call the actual implementation of the functionalities of the command
        self.redoIt()

    def undoIt(self):
        """
        Method that is called when the command is undone by the CTRL + Z or edit undo menu action
        """
        pass

    def redoIt(self):
        """
        Method that is called when the command is redone by the CTRL + Y or edit redo menu action.
        Here must be the actual logic of the functionalities
        """
        pass

    def isUndoable(self):
        """
        Method that is called after the doIt method. It helps maya understand if it needs to add the undoIt and
        redoIt action to the undoStack.
        As a suggestion, always create a command that is undoable
        :return: (bool): True or False whether the command is undoable or not. Defaults to False
        """
        return True

    @staticmethod
    def creator():
        return ommpx.asMPxPtr(MiniCommand())

    @staticmethod
    def create_syntax():
        """
        This method is only called if it is given as an argument in the initialize function call
        :return: (:obj: om.MSyntax):
        """
        syntax = om.MSyntax()

        # specify if the command can be executed with the edit flag and the query flag
        syntax.enableEdit(True)
        syntax.enableQuery(True)

        # add the flags, remember you can add a short name, a long name and a type
        # syntax.addFlag(MiniCommand.EXAMPLE_FLAGS[0], MiniCommand.EXAMPLE_FLAGS[1], om.MSyntax.kString)

        # to add a tuple with multiple values you could use the following syntax. Notice only 6 positional arguments
        # are allowed in a flag
        syntax.addFlag(
            MiniCommand.EXAMPLE_FLAGS[0], MiniCommand.EXAMPLE_FLAGS[1], om.MSyntax.kString, om.MSyntax.kDouble)

        # in order to have directly the selection list from the name of an object you could use the
        syntax.setObjectType(om.MSyntax.kSelectionList)
        # in order to get the scene selection list you must set this method to true
        syntax.useSelectionAsDefault(True)

        # if you want to specify a MINIMUM and a MAXIMUM of selected items you could use this expression
        # syntax.setObjectType(om.MSyntax.kSelectionList, 3, 3) or None, None by default that means no limit

        # add positional arguments
        syntax.addArg(om.MSyntax.kString)
        return syntax


def initializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin, MiniCommand.VENDOR, MiniCommand.VERSION)
    try:
        plugin_fn.registerCommand(MiniCommand.COMMAND_NAME, MiniCommand.creator, MiniCommand.create_syntax)
    except:
        om.MGlobal.displayError("Failed to register command: " + MiniCommand.COMMAND_NAME)


def uninitializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(MiniCommand.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister command: " + MiniCommand.COMMAND_NAME)


if __name__ == '__main__':
    """
    Just development 
    """
    import maya.cmds as mc

    plugin_file_name = "command_boilerplate1.py"

    # a new scene is need because there mustn't be any created command in the undoStack
    mc.file(new=True, force=True)

    # unload + load
    if mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.unloadPlugin(plugin_file_name)
    if not mc.pluginInfo(plugin_file_name, q=True, loaded=True):
        mc.loadPlugin(plugin_file_name)

    # add a simply set up to test the command
    mc.miniCommand()
