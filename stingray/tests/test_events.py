
import numpy as np
import os
import pytest

from ..events import EventList
from ..lightcurve import Lightcurve

curdir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(curdir, 'data')

_H5PY_INSTALLED = True

try:
    import h5py
except ImportError:
    _H5PY_INSTALLED = False


class TestEvents(object):
	
	@classmethod
	def setup_class(self):
		self.time = [0.5, 1.5, 2.5, 3.5]
		self.counts = [3000, 2000, 2200, 3600]
		self.spectrum = [[1, 2, 3, 4, 5, 6],[1000, 2040, 1000, 3000, 4020, 2070]]

	def test_to_lc(self):
		"""
		Create a light curve from event list
		"""
		ev = EventList(self.time)
		lc = ev.to_lc(1)

	def test_set_times(self):
		"""
		Set photon arrival times for an event list 
		from light curve.
		"""
		lc = Lightcurve(self.time, self.counts)
		ev = EventList()
		ev.set_times(lc)

	def test_set_times_with_spline(self):
		"""
		Set photon arrival times, with use_spline option
		enabled.
		"""
		lc = Lightcurve(self.time, self.counts)
		ev = EventList()
		ev.set_times(lc, use_spline = True)

	def test_recover_lc(self):
		"""
		Test that the original light curve can be recovered from 
		event list, which was used to simulate it.
		"""
		lc = Lightcurve(self.time, self.counts)
		ev = EventList()
		ev.set_times(lc)

		lc_rcd = ev.to_lc(dt=1, tstart=0, tseg=4)
		assert np.all(np.abs(lc_rcd.counts - lc.counts) < 3 * np.sqrt(lc.counts))

	def test_set_pha(self):
		"""
		Assign photon energies to an event list.
		"""
		ev = EventList(ncounts=100)
		ev.set_pha(self.spectrum)

	def test_set_pha_with_1d_spectrum(self):
		"""
		Test that set_pha() method raises index
		error exception is spectrum is 1-d. 
		"""
		ev = EventList(ncounts=100)
		with pytest.raises(IndexError):
			ev.set_pha(self.spectrum[0])

	def test_set_pha_with_wrong_spectrum_type(self):
		"""
		Test that set_pha() method raises type error
		exception when wrong sepctrum type is supplied.
		"""
		ev = EventList(ncounts=100)
		with pytest.raises(TypeError):
			ev.set_pha(1)

	def test_set_pha_with_counts_not_set(self):
		ev = EventList()
		ev.set_pha(self.spectrum)

	def test_compare_pha(self):
		"""
		Compare the simulated energy distribution to actual distribution.
		"""
		fluxes = np.array(self.spectrum[1])
		ev = EventList(ncounts=1000)
		ev.set_pha(self.spectrum)
		pha = [int(p) for p in ev.pha]

		# Histogram pha to get shape approximation
		gen_pha = ((np.array(pha) - 1) / 1).astype(int)
		lc = np.bincount(pha)

		# Remove first entry as it contains occurences of '0' element
		lc = lc[1:len(lc)]

		# Calculate probabilities and compare
		lc_prob = (lc/float(sum(lc)))
		fluxes_prob = fluxes/float(sum(fluxes))
		
		assert np.all(np.abs(lc_prob - fluxes_prob) < 3 * np.sqrt(fluxes_prob))

	def test_io_with_ascii(self):
		ev = EventList(self.time)
		ev.write('ascii_ev.txt',format_='ascii')
		ev = ev.read('ascii_ev.txt', format_='ascii')
		assert np.all(ev.time == self.time)
		os.remove('ascii_ev.txt')

	def test_io_with_pickle(self):
		ev = EventList(self.time)
		ev.write('ev.pickle', format_='pickle')
		ev = ev.read('ev.pickle',format_='pickle')
		assert np.all(ev.time == self.time)
		os.remove('ev.pickle')

	def test_io_with_hdf5(self):
		ev = EventList(time=self.time)
		ev.write('ev.hdf5', format_='hdf5')

		if _H5PY_INSTALLED:
			ev = ev.read('ev.hdf5',format_='hdf5')
			assert np.all(ev.time == self.time)
			os.remove('ev.hdf5')

		else:
			ev = ev.read('ev.pickle',format_='pickle')
			assert np.all(ev.time == self.time)
			os.remove('ev.pickle')

	def test_io_with_fits(self):
		ev = EventList(time = self.time)
		ev.write('ev.fits', format_='fits')
		ev = ev.read('ev.fits', format_='fits')
		assert np.all(ev.time == self.time)
		os.remove('ev.fits')

	def test_fits_with_standard_file(self):
		"""
		Test that fits works with a standard event list
		file.
		"""
		fname = os.path.join(datadir, 'monol_testA.evt')
		ev = EventList()
		ev = ev.read(fname, format_='fits')

	def test_io_with_wrong_format(self):
		"""
		Test that io methods raise Key Error when
		wrong format is provided.
		"""
		ev = EventList()
		with pytest.raises(KeyError):
			ev.write('ev.pickle', format_="unsupported")
			ev.read('ev.pickle', format_="unsupported")
			