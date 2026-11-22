import pytest

import econ_agent_harness.pipeline
import econ_agent_harness.setup
import econ_agent_harness.verify
import economic_libraries.auto_econ_sentiment.example1
import economic_libraries.auto_econ_sentiment.example2
import economic_libraries.econ_pdf_extract.example1
import economic_libraries.econ_pdf_extract.example2
import economic_libraries.linked_demo.demo
import economic_libraries.paths
import economic_libraries.reproducible_econ.example1
import economic_libraries.reproducible_econ.example2
import economic_libraries.stats_transformer.example1
import economic_libraries.stats_transformer.example2

STUB_MODULES = (
    econ_agent_harness.setup,
    econ_agent_harness.pipeline,
    econ_agent_harness.verify,
)


def test_run_stubs_raise():
    for module in STUB_MODULES:
        try:
            module.run()
        except NotImplementedError:
            pass
        else:
            raise AssertionError(f"{module.__name__}.run() should raise NotImplementedError")


IMPLEMENTED_MODULES = (
    economic_libraries.auto_econ_sentiment.example1,
    economic_libraries.auto_econ_sentiment.example2,
    economic_libraries.econ_pdf_extract.example1,
    economic_libraries.econ_pdf_extract.example2,
    economic_libraries.reproducible_econ.example1,
    economic_libraries.reproducible_econ.example2,
    economic_libraries.stats_transformer.example1,
    economic_libraries.stats_transformer.example2,
)


NS_RAW_FILES = (
    "NominalYields.parquet.gzip",
    "RealYields.parquet.gzip",
    "FOMCmeetings.parquet.gzip",
    "ABJ-2024-monetary-policy-surprises_Data.parquet.gzip",
)


def test_implemented_examples_run():
    for module in IMPLEMENTED_MODULES:
        module.run()


def test_linked_demo_runs():
    ns_dir = economic_libraries.paths.PROJECT_ROOT / "data/raw/nakamura_steinsson_2018"
    if not all((ns_dir / f).is_file() for f in NS_RAW_FILES):
        pytest.skip("Nakamura and Steinsson raw data absent (fresh clone)")
    economic_libraries.linked_demo.demo.LinkedDemo().run()
