# -*- coding: UTF-8 -*-
import logging
import click
import pretty_cron
import ast
import sys
import json
from typing import Any

if sys.version_info < (3, 4):
    print("To use this script you need python 3.4 or newer, got %s" %
          sys.version_info)
    sys.exit(1)

import xiaomiplug  # noqa: E402

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(xiaomiplug.Plug)


@click.group(invoke_without_command=True)
@click.option('--ip', envvar="XIAOMIPLUG_IP")
@click.option('--token', envvar="XIAOMIPLUG_TOKEN")
@click.option('-d', '--debug', default=False, count=True)
@click.option('--id-file', type=click.Path(dir_okay=False, writable=True),
              default='/tmp/xiaomiplug.seq')
@click.pass_context
def cli(ctx, ip: str, token: str, debug: int, id_file: str):
    """A tool to command Xiaomi Smart Plug."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    # if we are scanning, we do not try to connect.
    if ctx.invoked_subcommand == "discover":
        return

    if ip is None or token is None:
        click.echo("You have to give ip and token!")
        sys.exit(-1)

    start_id = manual_seq = 0
    try:
        with open(id_file, 'r') as f:
            x = json.load(f)
            start_id = x.get("seq", 0)
            manual_seq = x.get("manual_seq", 0)
            _LOGGER.debug("Read stored sequence ids: %s" % x)
    except (FileNotFoundError, TypeError) as ex:
        _LOGGER.error("Unable to read the stored msgid: %s" % ex)
        pass

    dev = xiaomiplug.Plug(ip, token, start_id, debug)
    dev.manual_seqnum = manual_seq
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)
        cleanup(dev, id_file=id_file)


@cli.resultcallback()
@pass_dev
def cleanup(dev: xiaomiplug.Plug, **kwargs):
    id_file = kwargs['id_file']
    seqs = {'seq': dev.raw_id, 'manual_seq': dev.manual_seqnum}
    _LOGGER.debug("Writing %s to %s" % (seqs, id_file))
    with open(id_file, 'w') as f:
        json.dump(seqs, f)
    #with open(id_file, 'w') as f:
    #    f.write(str(dev.raw_id))


@cli.command()
def discover():
    """Search for robots in the network."""
    xiaomiplug.Plug.discover()


@cli.command()
@pass_dev
def start(dev: xiaomiplug.Plug):
    """Power on."""
    click.echo("Power on: %s" % dev.start())


@cli.command()
@pass_dev
def stop(dev: xiaomiplug.Plug):
    """Power off."""
    click.echo("Power off: %s" % dev.stop())


@cli.command()
@click.argument('cmd', required=True)
@click.argument('parameters', required=False)
@pass_dev
def raw_command(dev: xiaomiplug.Plug, cmd, parameters):
    """Run a raw command."""
    params = []  # type: Any
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo("Sending cmd %s with params %s" % (cmd, params))
    click.echo(dev.raw_command(cmd, params))


if __name__ == "__main__":
    cli()
