import os
import platform
import sys
import traceback

import discord

from kithscord import common, util


class ArgError(Exception):
    pass


class UserCommand:
    """
    Base class to handle user commands.
    """

    def __init__(self):
        """
        Initialise UserCommand class
        """
        # Create a dictionary of command names and respective handler functions
        self.cmds_and_funcs = {}
        for i in dir(self):
            if i.startswith("cmd_"):
                self.cmds_and_funcs[i[len("cmd_") :]] = self.__getattribute__(i)

        # Avoid PyCharm shouting that member variables can't be declared
        # outside __init__
        self.invoke_msg = None
        self.response = None
        self.args = None
        self.string = None

    async def handle_cmd(self, invoke_msg: discord.Message, resp_msg: discord.Message):
        """
        Calles the appropriate sub function to handle commands.
        Must return True on successful command execution, False otherwise
        """
        self.invoke_msg = invoke_msg
        self.response = resp_msg

        cmd_str = invoke_msg.content[len(common.PREFIX) :].strip()
        self.args = cmd_str.split()
        cmd = self.args.pop(0)
        self.string = cmd_str[len(cmd) :].strip()

        util.log(f"Command invoked by {invoke_msg.author}: {cmd_str}")

        try:
            await self.cmds_and_funcs[cmd]()

        except Exception as exc:
            if isinstance(exc, ArgError):
                title = "Incorrect amount of argument(s)!"
                msg = exc.args[0]

            elif isinstance(exc, KeyError):
                title = "Unrecognized command!"
                msg = (
                    f"Make sure that the command '{cmd}' exists, "
                    + "and you have the permission to use it"
                )

            else:
                error_tuple = (type(exc), exc, exc.__traceback__)
                title = "An exception occured while handling the command!"

                tbs = traceback.format_exception(*error_tuple)
                # Pop out the first entry in the traceback, because that's
                # this function call itself
                tbs.pop(1)

                elog = "".join(tbs).replace(os.getcwd(), "Kithscord")
                if platform.system() == "Windows":
                    elog = elog.replace(os.path.dirname(sys.executable), "Python")

                util.log(f"Error: \n" + elog)
                msg = util.code_block(elog)

            await util.edit_embed(resp_msg, title, msg, 0xFF0000)

    def check_args(self, minarg, maxarg=None):
        """
        A utility for a function to check that the correct number of args were
        passed
        """
        exp = f"between {minarg} and {maxarg}"
        if maxarg is None:
            exp = maxarg = minarg

        got = len(self.args)
        if not (minarg <= got <= maxarg):
            raise ArgError(
                f"The number of arguments must be {exp} but {got} were given"
            )

    async def cmd_version(self):
        """
        Implement kh!version, for check version
        """
        self.check_args(0)
        await util.edit_embed(
            self.response,
            "Version",
            util.run_kcr("-v") + f"Kithscord Version {common.VERSION}",
        )

    async def cmd_lex(self):
        """
        Implement kh!lex, to lex kithare source
        """
        code = self.string.strip().strip("`")
        with open("tempfile", "w", encoding="utf-8") as f:
            f.write(code)

        try:
            await util.edit_embed(
                self.response,
                "Lexed Kithare output",
                util.code_block(util.run_kcr("--tokens", "--timer", "--nocolor", "tempfile")),
            )
        finally:
            os.remove("tempfile")

    async def cmd_parse(self):
        """
        Implement kh!lex, to lex kithare source
        """
        code = self.string.strip().strip("`")
        with open("tempfile", "w", encoding="utf-8") as f:
            f.write(code)

        try:
            await util.edit_embed(
                self.response,
                "Parsed Kithare output",
                util.code_block(util.run_kcr("--ast", "--timer", "--nocolor", "tempfile")),
            )
        finally:
            os.remove("tempfile")
