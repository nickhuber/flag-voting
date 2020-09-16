from django.test import TestCase

from vote.models import Flag


class FlagSVGTestCase(TestCase):
    def test_title_remove(self):
        f = Flag(svg="<svg><title>Test</title></svg>")
        f.clean()
        self.assertEqual(f.svg, "<svg></svg>")
