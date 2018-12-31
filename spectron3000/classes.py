

import base64
import io
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from plotly import graph_objs as go
from lmfit.models import GaussianModel

from spectron3000 import utils


@dataclass
class Spectrum:
    x: np.array
    y: np.array
    comment: str = "Observation"

    @classmethod
    def from_upload(cls, contents, filename):
        """
        Method for creating a Spectrum object from the Dash upload form.
        :param contents: data stream from Dash upload form
        :param filename: str filename
        :return: Spectrum object
        """
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        # Here pandas is simply being used as a parser...
        # It's not great, but I'd need to figure out how the decoded
        # string works before I can write my own.
        # TODO - write own parser and replace pandas here
        df = pd.read_csv(
            io.StringIO(decoded.decode("utf-8")),
            sep="\t"
        )
        x = df[df.columns[0]].values
        y = df[df.columns[1]].values
        spec_obj = cls(x, y, os.path.basename(filename))
        return spec_obj

    def create_plot(self):
        """
        Create a Plotly scatter trace for visualization.
        :return: Scatter object
        """
        trace = go.Scatter(
            x=self.x,
            y=self.y,
            name=self.comment,
            opacity=0.7
        )
        return trace

    def save_table(self, filepath):
        if hasattr(self, "table"):
            self.table.to_csv(
                filepath,
                index=False,
            )


@dataclass
class Catalog:
    frequency: np.array
    intensity: np.array
    state_energies: np.array
    molecule: str
    temperature: float = 300.0
    column_density: float = 1e15
    doppler: float = 5.0
    Q: float = 1.0

    @classmethod
    def from_upload(cls, contents, filename):
        """
        Method for creating a Catalog object from the Dash upload form.
        :param contents: data stream from Dash upload form
        :param filename: str filename
        :return: Spectrum object
        """
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        # Here pandas is simply being used as a parser...
        # It's not great, but I'd need to figure out how the decoded
        # string works before I can write my own.
        # TODO - write own parser and replace pandas here
        df = pd.read_fwf(
            io.StringIO(decoded.decode("utf-8")),
            widths=[13, 8, 8, 2, 10, 3, 7, 4, 2, 2, 2, 8, 2, 2],
            header=None
        )
        df.columns = [
            "Frequency",
            "Uncertainty",
            "Intensity",
            "DoF",
            "Lower state energy",
            "Degeneracy",
            "ID",
            "Coding",
            "N'",
            "F'",
            "J'",
            "N''",
            "F''",
            "J''"
        ]
        df["Upper state"] = utils.MHz2cm(df["Frequency"]) + df["Lower state energy"]
        df["Upper state Kelvin"] = df["Upper state"] / utils.kbcm
        pack = {
            "frequency": df["Frequency"].astype(float),
            "intensity": 10**df["Intensity"].astype(float),
            "molecule": os.path.basename(filename).split(".")[0],
            "state_energies": df["Upper state Kelvin"].astype(float)
        }
        cat_obj = cls(**pack)
        return cat_obj

    def generate_spectrum(self, spec_x):
        """
        Generate a synthetic spectrum using the catalog data. Each frequency is represented
        by a Gaussian line profile, with the width corresponding to the Doppler width in km/s.

        :param spec_x: np.array corresponding to the frequencies to be evaluated
        :return: np.array containing y values
        """
        model = GaussianModel()
        spec_y = np.zeros(len(spec_x))
        spec_x = np.array(spec_x)
        self.Q = utils.partition_function(self.state_energies, self.temperature)
        self.column_density = float(self.column_density)
        I = utils.I2S(self.intensity, self.Q, self.frequency, self.state_energies, self.temperature)
        flux = utils.N2flux(
            self.column_density,
            I,
            self.frequency,
            self.Q,
            self.state_energies,
            self.temperature
        )
        dopp_freq = utils.dop2freq(self.doppler, self.frequency)
        amplitudes = flux / np.sqrt(2. * np.pi**2. * dopp_freq)
        # Frequency, doppler shift in frequency, amplitude
        for c, w, a in zip(self.frequency, dopp_freq, amplitudes):
            spec_y += model.eval(
                x=spec_x,
                center=c,
                sigma=w,
                amplitude=a
            )
        return spec_y

    def to_table_format(self):
        """
        Puts the catalog data into DataTable format.
        :return: dict corresponding to everything in the class except the catalog lines
        """
        ignore = ["frequency", "intensity", "state_energies"]
        data = {key: value for key, value in self.__dict__.items() if key not in ignore}
        return data


def process_upload(filestream, filename):
    spec_ext = [".txt", ".spec", ".csv"]
    cat_ext = [".lin", ".cat"]
    if any(ext in filename for ext in spec_ext) is True:
        parser = Spectrum.from_upload
    elif any(ext in filename for ext in cat_ext) is True:
        parser = Catalog.from_upload
    return parser(filestream, filename)
