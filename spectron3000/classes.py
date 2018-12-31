

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
        x = df[df.columns[0]]
        y = df[df.columns[1]]
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
    molecule: str
    temperature: float = 300.0
    density: float = 1e15
    width: float = 5.0

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
        pack = {
            "frequency": df["Frequency"].values,
            "intensity": 10**df["Intensity"].values,
            "molecule": os.path.basename(filename)
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
        params = model.make_params()
        spec_y = np.zeros(len(spec_x))
        for x, y in zip(self.frequency, self.intensity):
            params["center"] = x
            params["amplitude"] = (10**y) * (np.sqrt(2. * np.pi) * utils.dop2freq(self.width, x))
            params["sigma"] = utils.dop2freq(self.width, x)
            spec_y+=model.eval(params=params, x=spec_x)
        return spec_y

    def to_table_format(self):
        """
        Puts the catalog data into DataTable format.
        :return: dict corresponding to everything in the class except the catalog lines
        """
        ignore = ["frequency", "intensity"]
        data = {key: value for key, value in self.__dict__.values() if key not in ignore}
        return data
