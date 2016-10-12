#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CLI application."""

from math import log
from math import sqrt
import click

#: Kerbal g₀ value
KSP_G0 = 9.82


#: Kerbal bodies information
KSP_BODIES = {
    'kerbin': {
        'g0': 9.82,
        'std_grav_param': 3.5316423e12,
        'radius': 600000,
    },
    'mun': {
        'g0': 1.66,
        'radius': 200000,
        'std_grav_param': 6.5139178e10,
    },
}


@click.group()
def cli():
    pass


def _dv(empty, full, isp):
    return isp * KSP_G0 * log(full / empty)


def _twr(body, mass, thrust):
    return sum(thrust) / (mass * KSP_BODIES[body]['g0'])


def _orbital_spd(body, height):
    return sqrt(KSP_BODIES[body]['std_grav_param'] / (KSP_BODIES[body]['radius'] + height))


@click.command()
@click.argument('empty', type=click.FLOAT)
@click.argument('full', type=click.FLOAT)
@click.argument('isp', type=click.FLOAT)
def dv(empty, full, isp):
    """Compute stage Δv."""
    print('Δv = {} m/s'.format(round(_dv(empty, full, isp), 2)))


@click.command()
@click.argument('body', type=click.Choice(KSP_BODIES.keys()))
@click.argument('mass', type=click.FLOAT)
@click.argument('thrust', nargs=-1, type=click.FLOAT)
def twr(body, mass, thrust):
    """Compute stage TWR."""
    print('TWR = {}'.format(round(_twr(body, mass, thrust), 2)))


@click.command()
@click.argument('body', type=click.Choice(KSP_BODIES.keys()))
@click.argument('height', type=click.FLOAT)
def orbital_spd(body, height):
    """Compute speed for given orbit around a body."""
    print('Speed = {}'.format(round(_orbital_spd(body, height), 2)))


@click.command()
@click.argument('payload', type=click.FLOAT)
@click.argument('eng_mass', type=click.FLOAT)
@click.argument('eng_thrust', type=click.FLOAT)
@click.argument('eng_isp', type=click.FLOAT)
@click.argument('tank_dry', type=click.FLOAT)
@click.argument('tank_full', type=click.FLOAT)
@click.argument('n_tanks', type=click.FLOAT)
@click.option('--stacks', type=click.INT, default=1)
@click.option('--body', type=click.Choice(KSP_BODIES.keys()), default='kerbin')
def stage(payload, eng_mass, eng_thrust, eng_isp, tank_dry, tank_full, n_tanks, stacks, body):
    """Compute stage info for given configuration."""
    stack_dry = eng_mass + tank_dry * n_tanks
    stack_full = eng_mass + tank_full * n_tanks
    mass_dry = payload + stack_dry * stacks
    mass_full = payload + stack_full * stacks

    print('Dry mass:   {} t'.format(mass_dry))
    print('Total mass: {} t'.format(mass_full))
    print('Δv:         {} m/s'.format(round(_dv(mass_dry, mass_full, eng_isp), 2)))
    print('TWR:        {} ({})'.format(round(_twr(body, mass_full, [eng_thrust]), 2), body))


cli.add_command(dv)
cli.add_command(twr)
cli.add_command(stage)
cli.add_command(orbital_spd)


if __name__ == '__main__':
    cli()
