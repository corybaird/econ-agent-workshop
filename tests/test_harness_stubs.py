import econ_agent_harness.pipeline
import econ_agent_harness.setup
import econ_agent_harness.verify

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
