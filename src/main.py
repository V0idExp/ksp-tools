#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CLI application."""

from math import floor
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

#: Engines data
KSP_ENGINES = {
    # LV-T30 "Reliant"
    'lv-t30': {
        'isp_atm': 265.0,
        'isp_vac': 310.0,
        'mass': 1.25,
        'thrust_atm': 205.67e3,
        'thrust_vac': 240.0e3,
    },
    # LV-T45 "Swivel"
    'lv-t45': {
        'isp_atm': 250.0,
        'isp_vac': 320.0,
        'mass': 1.5,
        'thrust_atm': 168.75e3,
        'thrust_vac': 215.0e3,
    },
    # LV-909 "Terrier"
    'lv-909': {
        'isp_atm': 85.0,
        'isp_vac': 345.0,
        'mass': 0.5,
        'thrust_atm': 14.753e3,
        'thrust_vac': 60.0e3,
    },
}


@click.group()
def cli():
    pass


def _dv(empty, full, isp):
    return isp * KSP_G0 * log(full / empty)


def _twr(body, mass, thrust):
    return thrust / (mass * 1000 * KSP_BODIES[body]['g0'])


def _orbital_spd(body, height):
    return sqrt(KSP_BODIES[body]['std_grav_param'] / (KSP_BODIES[body]['radius'] + height))


def _engine_stats(engines):
    def thr_sum(spec):
        return sum(KSP_ENGINES[e]['thrust_{}'.format(spec)] for e in engines)

    def flow_sum(spec):
        return sum(
            KSP_ENGINES[e]['thrust_{}'.format(spec)] / KSP_ENGINES[e]['isp_{}'.format(spec)]
            for e in engines)

    thr_atm = thr_sum('atm')
    thr_vac = thr_sum('vac')
    isp_atm = thr_atm / flow_sum('atm')
    isp_vac = thr_vac / flow_sum('vac')

    return thr_atm, thr_vac, isp_atm, isp_vac


@click.command()
@click.argument('empty', type=click.FLOAT)
@click.argument('full', type=click.FLOAT)
@click.argument('isp', type=click.FLOAT)
def dv(empty, full, isp):
    """Compute Δv."""
    print('Δv = {} m/s'.format(round(_dv(empty, full, isp), 2)))


@click.command()
@click.argument('body', type=click.Choice(KSP_BODIES.keys()))
@click.argument('mass', type=click.FLOAT)
@click.argument('thrust', type=click.FLOAT)
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
@click.argument('tank_dry', type=click.FLOAT)
@click.argument('tank_full', type=click.FLOAT)
@click.argument('n_tanks', type=click.FLOAT)
@click.argument('engines', type=click.Choice(KSP_ENGINES.keys()), nargs=-1, required=True)
@click.option('--body', type=click.Choice(KSP_BODIES.keys()), default='kerbin')
def stage(payload, tank_dry, tank_full, n_tanks, engines, body):
    """Compute stage info for given configuration."""
    eng_mass = sum(KSP_ENGINES[e]['mass'] for e in engines)
    thr_atm, thr_vac, isp_atm, isp_vac = _engine_stats(engines)
    dry = payload + eng_mass + tank_dry * n_tanks
    full = payload + eng_mass + tank_full * n_tanks

    print('Dry mass:   {} t'.format(round(dry, 1)))
    print('Total mass: {} t'.format(round(full, 1)))
    print('Δv (atm):   {} m/s'.format(floor(_dv(dry, full, isp_atm))))
    print('Δv (vac):   {} m/s'.format(floor(_dv(dry, full, isp_vac))))
    print('TWR (atm):  {} ({})'.format(round(_twr(body, full, thr_atm), 2), body))
    print('TWR (vac):  {} ({})'.format(round(_twr(body, full, thr_vac), 2), body))


@click.command()
@click.argument('engine', type=click.Choice(KSP_ENGINES.keys()))
def mass_flow(engine):
    """Compute mass flow values for given engine."""
    result = (
        KSP_ENGINES[engine]['thrust_{}'.format('vac')] /
        (KSP_ENGINES[engine]['isp_{}'.format('vac')] * KSP_G0))

    print('Mass flow: {}'.format(round(result, 3)))


cli.add_command(dv)
cli.add_command(twr)
cli.add_command(stage)
cli.add_command(mass_flow)
cli.add_command(orbital_spd)


if __name__ == '__main__':
    cli()
