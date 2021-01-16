from nose import tools

import auto_qc.evaluate.exception
from auto_qc import object
from auto_qc.evaluate import error


@tools.raises(auto_qc.evaluate.exception.VersionNumberException)
def test_thresholds_version_number():
    """Test raises an error with an invalid version number."""
    object.Thresholds(version="0.1.0", thresholds=[])
