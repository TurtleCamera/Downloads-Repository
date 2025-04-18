export run_ac_gmd_mls_blocker_placement, run_qc_gmd_mls_blocker_placement, run_soc_gmd_mls_blocker_placement
export run_ac_gmd_mld_blocker_placement, run_soc_gmd_mld_blocker_placement
export run_gmd_mls_blocker_placement, run_gmd_mld_blocker_placement


"FUNCTION: run GMD mitigation with nonlinear ac equations"
function run_ac_gmd_mls_blocker_placement(file, optimizer; kwargs...)
    return run_gmd_mls_blocker_placement(file, _PM.ACPPowerModel, optimizer; kwargs...)
end

function run_ac_gmd_mld_blocker_placement(file, optimizer; kwargs...)
    return run_gmd_mld_blocker_placement(file, _PM.ACPPowerModel, optimizer; kwargs...)
end


"FUNCTION: run GMD mitigation with qc ac equations"
function run_qc_gmd_mls_blocker_placement(file, optimizer; kwargs...)
    return run_gmd_mls_blocker_placement(file, _PM.QCLSPowerModel, optimizer; kwargs...)
end


"FUNCTION: run GMD mitigation with second order cone relaxation"
function run_soc_gmd_mls_blocker_placement(file, optimizer; kwargs...)
    return run_gmd_mls_blocker_placement(file, _PM.SOCWRPowerModel, optimizer; kwargs...)
end

function run_soc_gmd_mld_blocker_placement(file, optimizer; kwargs...)
    return run_gmd_mld_blocker_placement(file, _PM.SOCWRPowerModel, optimizer; kwargs...)
end


function run_gmd_mls_blocker_placement(file, model_type::Type, optimizer; kwargs...)
    return _PM.run_model(
        file,
        model_type,
        optimizer,
        build_gmd_mls;
        ref_extensions = [
            ref_add_gmd!
        ],
        solution_processors = [
            solution_gmd!,
            solution_gmd_qloss!,
        ],
        kwargs...,
    )
end

function run_gmd_mld_blocker_placement(file, model_type::Type, optimizer; kwargs...)
    return _PM.run_model(
        file,
        model_type,
        optimizer,
        build_gmd_mld;
        ref_extensions = [
            ref_add_gmd!
        ],
        solution_processors = [
            solution_gmd!,
            solution_gmd_qloss!,
        ],
        kwargs...,
    )
end


"FUNCTION: build the ac minimum loadshed coupled with quasi-dc power flow problem
as a generator dispatch minimization and load shedding problem"
function build_gmd_mls_blocker_placement(pm::_PM.AbstractPowerModel; kwargs...)
# Reference:
#   built minimum loadshed problem specification corresponds to the "Model C4" of
#   Mowen et al., "Optimal Transmission Line Switching under Geomagnetic Disturbances", 2018.

    _PM.variable_bus_voltage(pm)
    _PM.variable_gen_power(pm)
    _PM.variable_branch_power(pm)
    _PM.variable_dcline_power(pm)

    _PM.variable_load_power_factor(pm, relax=true)
    _PM.variable_shunt_admittance_factor(pm, relax=true)

    variable_blocker_indicator(pm; relax=false)
    variable_dc_voltage(pm)
    variable_dc_line_flow(pm)
    variable_qloss(pm)
    variable_dc_current(pm)

    _PM.constraint_model_voltage(pm)

    for i in _PM.ids(pm, :ref_buses)
        _PM.constraint_theta_ref(pm, i)
    end

    for i in _PM.ids(pm, :bus)
        constraint_power_balance_shunt_gmd_mls(pm, i)
    end

    for i in _PM.ids(pm, :branch)

        _PM.constraint_ohms_yt_from(pm, i)
        _PM.constraint_ohms_yt_to(pm, i)

        _PM.constraint_voltage_angle_difference(pm, i)

        _PM.constraint_thermal_limit_from(pm, i)
        _PM.constraint_thermal_limit_to(pm, i)

        constraint_qloss_vnom(pm, i)
        constraint_dc_current_mag(pm, i)

    end

    for i in _PM.ids(pm, :gmd_bus)
        if i in _PM.ids(pm, :bus_blockers)
            constraint_dc_power_balance_blocker(pm, i)
        else
            constraint_dc_power_balance(pm, i)
        end
    end

    for i in _PM.ids(pm, :gmd_branch)
        constraint_dc_ohms(pm, i)
    end

    objective_gmd_min_mls(pm)

end


"FUNCTION: build the ac minimum loadshed coupled with quasi-dc power flow problem
as a maximum loadability problem with relaxed generator and bus participation"
function build_gmd_mld_blocker_placement(pm::_PM.AbstractPowerModel; kwargs...)
# Reference:
#   built maximum loadability problem specification corresponds to the "MLD" specification of
#   PowerModelsRestoration.jl (https://github.com/lanl-ansi/PowerModelsRestoration.jl/blob/master/src/prob/mld.jl)

    variable_blocker_indicator(pm; relax=false)
    _PMR.variable_bus_voltage_indicator(pm, relax=true)
    _PMR.variable_bus_voltage_on_off(pm)

    _PM.variable_gen_indicator(pm, relax=true)
    _PM.variable_gen_power_on_off(pm)

    _PM.variable_branch_power(pm)
    _PM.variable_dcline_power(pm)

    _PM.variable_load_power_factor(pm, relax=true)
    _PM.variable_shunt_admittance_factor(pm, relax=true)

    variable_dc_voltage(pm)
    variable_dc_line_flow(pm)
    variable_qloss(pm)
    variable_dc_current(pm)

    _PMR.constraint_bus_voltage_on_off(pm)

    for i in _PM.ids(pm, :ref_buses)
        _PM.constraint_theta_ref(pm, i)
    end

    for i in _PM.ids(pm, :gen)
        _PM.constraint_gen_power_on_off(pm, i)
    end

    for i in _PM.ids(pm, :bus)
        constraint_power_balance_shed_gmd(pm, i)
    end

    for i in _PM.ids(pm, :branch)
        _PM.constraint_ohms_yt_from(pm, i)
        _PM.constraint_ohms_yt_to(pm, i)

        _PM.constraint_voltage_angle_difference(pm, i)

        _PM.constraint_thermal_limit_from(pm, i)
        _PM.constraint_thermal_limit_to(pm, i)

        constraint_qloss_vnom(pm, i)
        constraint_dc_current_mag(pm, i)

    end

    for i in _PM.ids(pm, :dcline)
        _PM.constraint_dcline_power_losses(pm, i)
    end

    for i in _PM.ids(pm, :gmd_bus)
        if i in _PM.ids(pm, :bus_blockers)
            constraint_dc_power_balance_blocker(pm, i)
        else
            constraint_dc_power_balance(pm, i)
        end
    end

    for i in _PM.ids(pm, :gmd_branch)
        constraint_dc_ohms(pm, i)
    end

    constraint_load_served(pm, 0.95)

    # _PMR.objective_max_loadability(pm)
    objective_blocker_placement_cost(pm)
end
