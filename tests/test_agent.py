def test_agent_import():
    from econ_agent_harness import agent
    assert agent.ROOT.exists()
