
""" units.py

    Routines for performing unit conversions and quantities
    that are often used in spectroscopy.
"""

import json

import numpy as np
from scipy import constants


kbcm = constants.value("Boltzmann constant in inverse meters per kelvin") / 100.
avo = constants.Avogadro
eha = constants.value("Hartree energy")
harm = constants.value("hartree-inverse meter relationship")
jm = constants.value("joule-inverse meter relationship")


def kappa(A, B, C):
    # Ray's asymmetry parameter
    return (2*B - A - C) / (A - C)


def rotcon2pmi(rotational_constant):
    """ Convert rotational constants in units of MHz to
        Inertia, in units of amu A^2.

        The conversion factor is adapted from:
        Oka & Morino, JMS (1962) 8, 9-21
        This factor comprises h / pi^2 c.

        :param rotational_constant: rotational constant in MHz
        :return:
    """
    return 1 / (rotational_constant / 134.901)


def partition_function(state_energies, temperature):
    """
    Calculate the partition function for a set of state energies and a given
    temperature.
    :param state_energies: np.array of upper state energies
    :param temperature: float value for temperature in K
    :return: partition function
    """
    return np.sum(boltzmann_factor(state_energies * kbcm, temperature))


def inertial_defect(rotational_constants):
    """ Calculates the inertial defect, given three
        rotational constants in MHz. The ordering does not
        matter because the values are sorted.

        This value is I_c - I_a - I_b; a planar molecule
        is strictly zero.
    """
    # Ensure the ordering is A,B,C
    rotational_constants = np.sort(rotational_constants)[::-1]
    # Convert to principal moments of inertia
    pmi = rotcon2pmi(rotational_constants)
    return pmi[2] - pmi[0] - pmi[1]


def hartree2wavenumber(hartree):
    """
    Convert Hartrees to wavenumbers.
    :param hartree: float
    :return: corresponding value in 1/cm
    """
    return hartree * (harm / 100.)


def kjmol2wavenumber(kj):
    """
    Convert kJ/mol to wavenumbers
    :param kj: float
    :return: corresponding value in 1/cm
    """
    return kj * (jm / 100.) / (avo * 1000.)


def MHz2cm(frequency):
    """
    Convert MHz to wavenumbers
    :param frequency: float
    :return: corresponding value in 1/cm
    """
    return (frequency / 1000.) / (constants.c / 1e7)


def cm2MHz(wavenumber):
    """
    Convert wavenumbers to MHz
    :param wavenumber: float
    :return: corresponding value in MHz
    """
    return (wavenumber * (constants.c / 1e7)) * 1000.


def hartree2kjmol(hartree):
    """
    Convert Hartrees to kJ/mol.
    :param hartree: float
    :return: converted value in kJ/mol
    """
    return hartree * (eha * avo / 1000.)


def wavenumber2kjmol(wavenumber):
    """
    Convert wavenumbers to kJ/mol.
    :param wavenumber: float
    :return: converted value in kJ/mol
    """
    return wavenumber / (jm / 100.) / (avo * 1000.)


def T2wavenumber(T):
    """
    Convert temperature in Kelvin to wavenumbers.
    :param T: float
    :return: corresponding value in 1/cm
    """
    return T * kbcm


def wavenumber2T(wavenumber):
    """
    Convert wavenumbers to Kelvin
    :param wavenumber: float
    :return: corresponding value in K
    """
    return wavenumber / kbcm


""" 
    Astronomy units 

    Conversions and useful expressions
"""


def dop2freq(velocity, frequency):
    """
    Calculates the expected frequency in MHz based on a
    Doppler shift in km/s and a center frequency.
    :param velocity: float
    :param frequency: float
    :return: Doppler shifted frequency in MHz
    """
    # Frequency given in MHz, Doppler_shift given in km/s
    # Returns the expected Doppler shift in frequency (MHz)
    return ((velocity * 1000. * frequency) / constants.c)


def freq2vel(frequency, offset):
    """
    Calculates the Doppler shift in km/s based on a center
    frequency in MHz and n offset frequency in MHz (delta nu)
    :param frequency: float
    :param offset: float
    :return: Doppler shift in km/s
    """
    return ((constants.c * offset) / frequency) / 1000.


def gaussian_fwhm(sigma):
    """
        Calculate the full-width half maximum
        value assuming a Gaussian function.

        parameters:
        --------------
        sigma - float for width

        returns:
        --------------
        fwhm - float value for full-width at half-max
    """
    return 2. * np.sqrt(2. * np.log(2.)) * sigma


def gaussian_height(amplitude, sigma):
    """
        Calculate the height of a Gaussian distribution,
        based on the amplitude and sigma. This value
        corresponds to the peak height at the centroid.

        parameters:
        ----------------
        amplitude - float
        sigma - float

        returns:
        ----------------
        h - float
    """
    h = amplitude / (np.sqrt(2. * np.pi) * sigma)
    return h


def gaussian_integral(amplitude, sigma):
    """
    Calculate the integral of a Gaussian analytically using
    the amplitude and sigma.
    :param amplitude: amplitude of the Gaussian
    :param sigma: width of the Gaussian
    :return: integrated area of the Gaussian
    """
    integral = amplitude * np.sqrt(2. * np.pi**2. * sigma)
    return integral


def N2flux(N, S, v, Q, E, T):
    """
    Calculate the expected flux in Jy for a given set of parameters.
    :param N: column density in cm^-2
    :param S: intrinsic line strength; Su^2
    :param v: transition frequency in MHz
    :param Q: rotational partition function
    :param E: upper state energy
    :param T: temperature
    :return: integrated flux in Jy
    """
    numerator = (N * S * (v / 1e3)**3.) / 1e20
    denominator = 2.04 * Q * np.exp(E / T)
    flux = numerator / denominator
    return flux


def boltzmann_factor(E, T):
    """
    Calculate the Boltzmann weight for a given state energy and
    temperature.
    :param E: state energy in 1/cm
    :param T: temperature in K
    :return: float Boltzmann factor
    """
    return np.exp(-E / (kbcm * T))


def I2S(I, Q, frequency, E_upper, T):
    """
    Calculate the intrinsic line strength for a given transition frequency
    and intensity, and thermodynamic quantities like state energy, temperature,
    and partition function.
    :param I: transition intensity in nm^2 MHz
    :param Q: partition function
    :param frequency: transition frequency in MHz
    :param E_upper: upper state energy in K
    :param T: temperature in K
    :return: intrinsic line strength; Su^2
    """
    E_upper = E_upper * kbcm
    E_lower = MHz2cm(cm2MHz(E_upper) - frequency)
    A = I * Q
    B = (4.16231e-5 * frequency * (boltzmann_factor(E_lower, T) - boltzmann_factor(E_upper, T)))
    return A / B
