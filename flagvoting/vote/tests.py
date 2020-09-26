from django.test import TestCase

from vote.models import Flag


class FlagSVGTestCase(TestCase):
    def test_title_remove(self):
        f = Flag(svg="<svg><title>Test</title><g>foo</g></svg>")
        f.clean()
        self.assertEqual(
            f.svg,
            """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
 <g>foo</g>
</svg>
""",
        )
