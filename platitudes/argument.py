"""Functionality to customize and validate arguments."""

from .actions import make_datetime_action, make_path_action

DEFAULT_DATETIME_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]


class Argument:
    """`Argument` provides extended parsing and validation options."""

    def __init__(
        self,
        help: str | None = None,  # noqa: A002
        envvar: str | None = None,
        # Path
        exists: bool = False,
        file_okay: bool = True,
        dir_okay: bool = True,
        writable: bool = False,
        readable: bool = False,
        resolve_path: bool = False,
        # DateTime
        formats: list[str] | None = None,
    ):
        """


        `Argument` is always added inside an Annotated type and provides the following
        functionality:

        - Adding help lines to the output of the `--help` option.
        - Reading parameters from environment variables.
        - Adding validation options for parsed
          [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#basic-use)
        - Modifying the accepted
          [datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime-objects)
          for the CLI.

        Parameters
        ----------
        help: str
            The help string that will be presented by the CLI help.
        envvar
            If supplied we will try to get the value of the parameter
            from the environment variable being pointed at.
        exists
            If `True` argument parsing will file if the path provided
            corresponds to a non-existent file or directory.
        file_okay
            If `False` argument parsing will file if the path provided
            corresponds to a file.
        dir_okay
            If `False` argument parsing will file if the path provided
            corresponds to a directory.
        writable
            Fail argument parsing if the path doesn't correspond to a
            writable file or directory.
        readable
            Fail argument parsing if the path doesn't correspond to a
            readable file or directory.
        resolve_path
            Whether to resolve the path supplied before passing it to the
            function.
        formats
            A list of format strings that can be used in the CLI to enter
            timestamps

        """
        self.help = help
        self.envvar = envvar

        # Only relevant if we are dealing with Paths
        self._path_action = make_path_action(
            exists,
            file_okay,
            dir_okay,
            writable,
            readable,
            resolve_path,
        )

        # Only relevant if we are dealing with Paths
        if formats is None:
            formats = DEFAULT_DATETIME_FORMATS
        self._datetime_action = make_datetime_action(formats)
