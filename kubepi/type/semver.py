from semver import parse
import click


class BasedVersionParamType(click.ParamType):
    name = "semver"

    def convert(self, value, param, ctx):
        try:
            parse(value)
            return(value)
        except TypeError:
            self.fail(
                '{value!r} is not a valid version, please use semver',
                param,
                ctx,
            )
        except ValueError:
            self.fail(f'{value!r} is not a valid version, please use semver',
                      param, ctx)
