from nose import tools

from auto_qc import object
from auto_qc.evaluate import error


@tools.raises(error.VersionNumberError)
def test_thresholds_version_number():
    """Test raises an error with an invalid version number."""
    object.Thresholds(version="0.1.0", thresholds=[])
