import pytest
import pyhf
import pyhf.infer.test_statistics
import logging


def test_q0(caplog):
    mu = 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    with caplog.at_level(logging.WARNING, "pyhf.infer.test_statistics"):
        pyhf.infer.test_statistics.q0(
            mu, data, model, init_pars, par_bounds, fixed_params
        )
        assert (
            "q0 test statistic only used for fit configuration with POI set to zero"
            in caplog.text
        )
        caplog.clear()


def test_qmu(caplog):
    mu = 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    with caplog.at_level(logging.WARNING, "pyhf.infer.test_statistics"):
        pyhf.infer.test_statistics.qmu(
            mu, data, model, init_pars, par_bounds, fixed_params
        )
        assert "qmu test statistic used for fit" in caplog.text
        caplog.clear()


def test_qmu_tilde(caplog):
    mu = 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    par_bounds[model.config.poi_index] = [-10, 10]
    with caplog.at_level(logging.WARNING, "pyhf.infer.test_statistics"):
        pyhf.infer.test_statistics.qmu_tilde(
            mu, data, model, init_pars, par_bounds, fixed_params
        )
        assert "qmu_tilde test statistic used for fit" in caplog.text
        caplog.clear()


def test_tmu(caplog):
    mu = 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    with caplog.at_level(logging.WARNING, "pyhf.infer.test_statistics"):
        pyhf.infer.test_statistics.tmu(
            mu, data, model, init_pars, par_bounds, fixed_params
        )
        assert "tmu test statistic used for fit" in caplog.text
        caplog.clear()


def test_tmu_tilde(caplog):
    mu = 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    par_bounds[model.config.poi_index] = [-10, 10]
    with caplog.at_level(logging.WARNING, "pyhf.infer.test_statistics"):
        pyhf.infer.test_statistics.tmu_tilde(
            mu, data, model, init_pars, par_bounds, fixed_params
        )
        assert "tmu_tilde test statistic used for fit" in caplog.text
        caplog.clear()


def test_no_poi_test_stats():
    spec = {
        "channels": [
            {
                "name": "channel",
                "samples": [
                    {
                        "name": "sample",
                        "data": [10.0],
                        "modifiers": [
                            {
                                "type": "normsys",
                                "name": "shape",
                                "data": {"hi": 0.5, "lo": 1.5},
                            }
                        ],
                    },
                ],
            }
        ]
    }
    model = pyhf.Model(spec, poi_name=None)

    test_poi = 1.0
    data = [12] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    with pytest.raises(pyhf.exceptions.UnspecifiedPOI) as excinfo:
        pyhf.infer.test_statistics.q0(
            test_poi, data, model, init_pars, par_bounds, fixed_params
        )
    assert (
        "No POI is defined. A POI is required for profile likelihood based test statistics."
        in str(excinfo.value)
    )

    with pytest.raises(pyhf.exceptions.UnspecifiedPOI) as excinfo:
        pyhf.infer.test_statistics.qmu(
            test_poi, data, model, init_pars, par_bounds, fixed_params
        )
    assert (
        "No POI is defined. A POI is required for profile likelihood based test statistics."
        in str(excinfo.value)
    )

    with pytest.raises(pyhf.exceptions.UnspecifiedPOI) as excinfo:
        pyhf.infer.test_statistics.qmu_tilde(
            test_poi, data, model, init_pars, par_bounds, fixed_params
        )
    assert (
        "No POI is defined. A POI is required for profile likelihood based test statistics."
        in str(excinfo.value)
    )

    with pytest.raises(pyhf.exceptions.UnspecifiedPOI) as excinfo:
        pyhf.infer.test_statistics.tmu(
            test_poi, data, model, init_pars, par_bounds, fixed_params
        )
    assert (
        "No POI is defined. A POI is required for profile likelihood based test statistics."
        in str(excinfo.value)
    )

    with pytest.raises(pyhf.exceptions.UnspecifiedPOI) as excinfo:
        pyhf.infer.test_statistics.tmu_tilde(
            test_poi, data, model, init_pars, par_bounds, fixed_params
        )
    assert (
        "No POI is defined. A POI is required for profile likelihood based test statistics."
        in str(excinfo.value)
    )


@pytest.mark.parametrize("test_stat", ["qtilde", "q"])
def test_get_teststat_by_name(test_stat):
    assert pyhf.infer.utils.get_test_stat(test_stat)


def test_get_teststat_error():
    with pytest.raises(pyhf.exceptions.InvalidTestStatistic):
        pyhf.infer.utils.get_test_stat("look at me i'm not real")


@pytest.mark.parametrize("return_fitted_pars", [False, True])
@pytest.mark.parametrize(
    "test_stat",
    [
        pyhf.infer.test_statistics.q0,
        pyhf.infer.test_statistics.qmu,
        pyhf.infer.test_statistics.qmu_tilde,
        pyhf.infer.test_statistics.tmu,
        pyhf.infer.test_statistics.tmu_tilde,
    ],
)
def test_return_fitted_pars(test_stat, return_fitted_pars):
    mu = 0.0 if test_stat is pyhf.infer.test_statistics.q0 else 1.0
    model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
    data = [9] + model.config.auxdata
    init_pars = model.config.suggested_init()
    par_bounds = model.config.suggested_bounds()
    fixed_params = model.config.suggested_fixed()

    result = test_stat(
        mu,
        data,
        model,
        init_pars,
        par_bounds,
        fixed_params,
        return_fitted_pars=return_fitted_pars,
    )
    if return_fitted_pars:
        assert len(result) == 2
        assert len(result[1]) == 2
        result, (pars_bestfit, pars_constrained_fit) = result
        assert len(pars_bestfit) == len(init_pars)
        assert len(pars_constrained_fit) == len(init_pars)
    assert result > -1e4  # >= 0 but with generous tolerance
