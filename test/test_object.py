import pytest

import auto_qc.evaluate.exception
from auto_qc import object


def test_thresholds_version_number():
    """Test raises an error with an invalid version number."""
    with pytest.raises(auto_qc.evaluate.exception.VersionNumberException):
        object.AutoQC(version="0.1.0", thresholds=[], data={})
