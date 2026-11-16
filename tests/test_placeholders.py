import econ_agent_harness.pipeline
import econ_agent_harness.setup
import econ_agent_harness.verify
import economic_libraries.auto_econ_sentiment.example1
import economic_libraries.auto_econ_sentiment.example2
import economic_libraries.econ_pdf_extract.example1
import economic_libraries.econ_pdf_extract.example2
import economic_libraries.reproducible_econ.example1
import economic_libraries.reproducible_econ.example2
import economic_libraries.stats_transformer.example1
import economic_libraries.stats_transformer.example2

MODULES = (
    econ_agent_harness.setup,
    econ_agent_harness.pipeline,
    econ_agent_harness.verify,
    economic_libraries.auto_econ_sentiment.example1,
    economic_libraries.auto_econ_sentiment.example2,
    economic_libraries.econ_pdf_extract.example1,
    economic_libraries.econ_pdf_extract.example2,
    economic_libraries.reproducible_econ.example1,
    economic_libraries.reproducible_econ.example2,
    economic_libraries.stats_transformer.example1,
    economic_libraries.stats_transformer.example2,
)


def test_run_stubs_raise():
    for module in MODULES:
        try:
            module.run()
        except NotImplementedError:
            pass
        else:
            raise AssertionError(f"{module.__name__}.run() should raise NotImplementedError")
