import unittest
from unittest.mock import Mock, ANY
from kauppa import Kauppa
from viitegeneraattori import Viitegeneraattori
from varasto import Varasto
from tuote import Tuote

class TestKauppa(unittest.TestCase):
    def setUp(self):
        self.pankki_mock = Mock()
        self.viitegeneraattori_mock = Mock()

        self.viitegeneraattori_mock.uusi.return_value = 42

        self.varasto_mock = Mock()
        saldot = {1: 10, 2: 10, 3: 0}
        tuotteet = {
            1: ("maito", 5),
            2: ("leipä", 3),
            3: ("Olut", 4),
        }

        def varasto_saldo(tuote_id):
            return saldot.get(tuote_id)

        def varasto_hae_tuote(tuote_id):
            tuote = tuotteet.get(tuote_id)
            if tuote is not None:
                return Tuote(tuote_id, *tuote)

        self.varasto_mock.saldo.side_effect = varasto_saldo
        self.varasto_mock.hae_tuote.side_effect = varasto_hae_tuote

        self.kauppa = Kauppa(
            self.varasto_mock, self.pankki_mock, self.viitegeneraattori_mock
        )
        self.kauppa.aloita_asiointi()

    def test_maksettaessa_ostos_pankin_metodia_tilisiirto_kutsutaan(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.tilimaksu("pekka", "12345")

        # varmistetaan, että metodia tilisiirto on kutsuttu
        self.pankki_mock.tilisiirto.assert_called()
        # toistaiseksi ei välitetä kutsuun liittyvistä argumenteista

    def test_maksettaessa_tilisiirto_kutsuu_oikeilla_parametreilla(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.tilimaksu("pekka", "12345")

        self.pankki_mock.tilisiirto.assert_called_with(
            "pekka", 42, "12345", "33333-44455", 5
        )

    def test_pystyy_ostaa_kahta_eri_tuotetta(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.lisaa_koriin(2)
        self.kauppa.tilimaksu("pekka", "12345")
        self.pankki_mock.tilisiirto.assert_called_with(
            "pekka", 42, "12345", "33333-44455", 8
        )

    def test_ostetaan_kaksi_samaa_tuotetta(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.lisaa_koriin(1)
        self.kauppa.tilimaksu("pekka", "12345")
        self.pankki_mock.tilisiirto.assert_called_with(
            "pekka", 42, "12345", "33333-44455", 10
        )

    def test_ostetaan_loppuunmyynty_tuote(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.lisaa_koriin(3)
        self.kauppa.tilimaksu("pekka", "12345")
        self.pankki_mock.tilisiirto.assert_called_with(
            "pekka", 42, "12345", "33333-44455", 5
        )

    def test_kauppa_pyytaa_uuden_viitenumeron_joka_maksutapahtumalle(self):
        self.viitegeneraattori_mock.uusi.side_effect = [42, 43]
        self.kauppa.lisaa_koriin(1)
        self.kauppa.tilimaksu("pekka", "12345")
        self.kauppa.lisaa_koriin(2)
        self.kauppa.tilimaksu("pekka", "12345")
        kutsut = self.pankki_mock.tilisiirto.call_args_list
        self.assertEqual(kutsut[0].args[1], 42)
        self.assertEqual(kutsut[1].args[1], 43)

    def test_poista_korista_poistaa_tuotteen_korista(self):
        self.kauppa.lisaa_koriin(1)
        self.kauppa.poista_korista(1)
        self.kauppa.tilimaksu("pekka", "12345")
        self.pankki_mock.tilisiirto.assert_called_with(
            "pekka", 42, "12345", "33333-44455", 0
        )

