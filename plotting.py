import matplotlib.pyplot as plt
import pandas
import scipy.stats
import Model
import StateEstimator
import stateUpdaters


# noinspection DuplicatedCode
def plot_all(file_name, confidence=0.95, show=True):
    """Plots all the graphs from a file

    Parameters
    ----------
    file_name : string
        The name of the file in which all the data is stored

    confidence : float, optional
        The confidence probability for the plots
        Defaults to 95%

    show : bool, optional
        If `True` then the plt.show method is called at the end.
        Useful to turn off when you want to add additional things
        Defaults to `True`
    """
    xls = pandas.ExcelFile(file_name)
    model = pandas.read_excel(xls, 'model')
    se = pandas.read_excel(xls, 'se')
    su = pandas.read_excel(xls, 'su')

    # Model
    ts_m = model['ts']
    Vs_m = model['V']
    Cgs_m = model['Ng'] * 180 / Vs_m
    Cfas_m = model['Nfa'] * 116 / Vs_m
    Ces_m = model['Ne'] * 46 / Vs_m
    Czs_m = model['Nz'] / Vs_m
    Cys_m = model['Ny'] / Vs_m
    Ts_m = model['T']
    pH_m = model['pH']

    # SE means
    ts = se['ts']
    Vs = se['V']
    Cgs = se['Ng'] * 180 / Vs
    Cfas = se['Nfa'] * 116 / Vs
    Ces = se['Ne'] * 46 / Vs
    Czs = se['Nz'] / Vs
    Cys = se['Ny'] / Vs
    Ts = se['T']

    # Standard deviation multiplier to get the correct confidence interval
    K = scipy.stats.norm.ppf(confidence)
    # SE covs
    Pgs = se['Ng_cov'] * 180 / Vs * K
    Pfas = se['Nfa_cov'] * 116 / Vs * K
    Pes = se['Ne_cov'] * 46 / Vs * K
    Pzs = se['Nz_cov'] / Vs * K
    Pys = se['Ny_cov'] / Vs * K
    PTs = se['T_cov']

    # Measured update values
    ts_meas = su['ts']
    Cg_meas = su['Cg']
    Cfa_meas = su['Cfa']
    Ce_meas = su['Ce']

    plt.figure(figsize=(20, 20))
    plt.rc("font", size=20)
    plt.subplot(2, 2, 1)
    plt.plot(ts_m, Cgs_m, "--")
    plt.plot(ts_m, Cgs, "-.")
    plt.plot(ts, Cgs + Pgs, 'tab:purple')
    plt.plot(ts, Cgs - Pgs, 'tab:purple')
    plt.plot(ts_meas, Cg_meas, '.')
    plt.title("Glucose")

    plt.subplot(2, 2, 2)
    plt.plot(ts_m, Cfas_m, "--")
    plt.plot(ts_m, Cfas, "-.")
    plt.plot(ts, Cfas + Pfas, 'tab:purple')
    plt.plot(ts, Cfas - Pfas, 'tab:purple')
    plt.plot(ts_meas, Cfa_meas, '.')
    plt.title("Fumaric")

    plt.subplot(2, 2, 3)
    plt.plot(ts_m, Ces_m, "--")
    plt.plot(ts_m, Ces, "-.")
    plt.plot(ts, Ces + Pes, 'tab:purple')
    plt.plot(ts, Ces - Pes, 'tab:purple')
    plt.plot(ts_meas, Ce_meas, '.')
    plt.title("Ethanol")

    plt.subplot(2, 2, 4)
    plt.plot(ts_m, Czs_m, "--")
    plt.plot(ts_m, Czs, "-.")
    plt.plot(ts, Czs + Pzs, 'tab:purple', label="Z")
    plt.plot(ts, Czs - Pzs, 'tab:purple')

    plt.plot(ts_m, Cys_m, "--")
    plt.plot(ts_m, Cys_m, "-.")
    plt.plot(ts, Cys + Pys, 'tab:pink', label="Y")
    plt.plot(ts, Cys - Pys, 'tab:pink')
    plt.title("Enzyme")
    plt.legend()

    # plt.subplot(3, 2, 5)
    # plt.plot(ts_m, Ts_m, "--")
    # plt.plot(ts, Ts + PTs)
    # plt.plot(ts, Ts - PTs)
    # plt.title("Temperature")
    #
    # plt.subplot(3, 2, 6)
    # plt.plot(ts_m, pH_m)
    # plt.title("pH")

    plt.savefig("results/all9.pdf")
    if show:
        plt.show()


def plot_live(ts,
              model_obj: Model.Model,
              se_obj: StateEstimator.StateEstimator,
              su_obj: {stateUpdaters.FakeStateUpdate, stateUpdaters.LabviewStateUpdate},
              confidence=0.95):
    """
    Parameters
    ----------
    ts : array_like
        List of times

    model_obj : Model.Model
        Model object

    se_obj : StateEstimator.StateEstimator
        State estimation object

    su_obj : {stateUpdaters.FakeStateUpdate,  stateUpdaters.LabviewStateUpdate}
        State updating object

    confidence : float, optional
        The confidence probability for the plots
        Defaults to 95%
    """
    model = model_obj.get_data()
    se = se_obj.get_data()
    if model.shape[0] > 3:
        model = model[3:]
        se = se[3:]
    su = su_obj.get_data()

    # Model
    # 'ts', 'Ng', 'Nx', 'Nfa', 'Ne', 'Nco', 'No', 'Nn', 'Na', 'Nb', 'Nz', 'Ny', 'V', 'Vg', 'T', 'pH'
    Vs_m = model[:, 11]
    Cgs_m = model[:, 0] * 180 / Vs_m
    Cfas_m = model[:, 2] * 116 / Vs_m
    Ces_m = model[:, 3] * 46 / Vs_m
    Czs_m = model[:, 9] / Vs_m
    Cys_m = model[:, 10] / Vs_m
    Ts_m = model[:, 13]
    pH_m = model[:, 14]
    ts_m = ts[:len(Vs_m)]

    # SE means
    Vs = se[:, 11]
    Cgs = se[:, 0] * 180 / Vs_m
    Cfas = se[:, 2] * 116 / Vs_m
    Ces = se[:, 3] * 46 / Vs_m
    Czs = se[:, 9] / Vs_m
    Cys = se[:, 10] / Vs_m
    Ts = se[:, 13]
    ts = ts_m

    # Standard deviation multiplier to get the correct confidence interval
    K = scipy.stats.norm.ppf(confidence)
    # SE covs
    Pgs = se[:, 14 + 0] * 180 / Vs * K
    Pfas = se[:, 14 + 2] * 116 / Vs * K
    Pes = se[:, 14 + 3] * 46 / Vs * K
    Pzs = se[:, 14 + 9] / Vs * K
    Pys = se[:, 14 + 10] / Vs * K
    PTs = se[:, 14 + 13]

    # Measured update values
    ts_meas = su_obj.get_times()
    ts_meas = ts_meas[ts_meas <= ts[-1]]
    Cg_meas = su[:, 0][:len(ts_meas)]
    Cfa_meas = su[:, 1][:len(ts_meas)]
    Ce_meas = su[:, 2][:len(ts_meas)]

    plt.subplot(3, 2, 1)
    plt.cla()
    plt.plot(ts_m, Cgs_m, "--")
    plt.plot(ts, Cgs + Pgs)
    plt.plot(ts, Cgs - Pgs)
    plt.plot(ts_meas, Cg_meas, '.')
    plt.title("Glucose")

    plt.subplot(3, 2, 2)
    plt.cla()
    plt.plot(ts_m, Cfas_m, "--")
    plt.plot(ts, Cfas + Pfas)
    plt.plot(ts, Cfas - Pfas)
    plt.plot(ts_meas, Cfa_meas, '.')
    plt.title("Fumaric")

    plt.subplot(3, 2, 3)
    plt.cla()
    plt.plot(ts_m, Ces_m, "--")
    plt.plot(ts, Ces + Pes)
    plt.plot(ts, Ces - Pes)
    plt.plot(ts_meas, Ce_meas, '.')
    plt.title("Ethanol")

    plt.subplot(3, 2, 4)
    plt.cla()
    plt.plot(ts_m, Czs_m, "--")
    plt.plot(ts, Czs + Pzs, label="Z+")
    plt.plot(ts, Czs - Pzs, label="Z-")

    plt.plot(ts_m, Cys_m, "--")
    plt.plot(ts, Cys + Pys, label="Y+")
    plt.plot(ts, Cys - Pys, label="Y-")
    plt.title("Enzyme")
    plt.legend()

    plt.subplot(3, 2, 5)
    plt.cla()
    plt.plot(ts_m, Ts_m, "--")
    plt.plot(ts, Ts + PTs)
    plt.plot(ts, Ts - PTs)
    plt.title("Temperature")

    plt.subplot(3, 2, 6)
    plt.cla()
    plt.plot(ts_m, pH_m)
    plt.title("pH")

    plt.pause(0.001)


def plot_data(file_name, show=True):
    """Plots state update data from a file

    Parameters
    ----------
    file_name : string
        The name of the file in which all the data is stored

    show : bool, optional
        If `True` then the plt.show method is called at the end.
        Useful to turn off when you want to add additional things
        Defaults to `True`
    """
    xls = pandas.ExcelFile(file_name)
    su = pandas.read_excel(xls, 'su')

    # Measured update values
    ts_meas = su['ts']
    Cg_meas = su['Cg']
    Cfa_meas = su['Cfa']
    Ce_meas = su['Ce']

    plt.figure(figsize=(10, 2))
    plt.subplot(1, 3, 1)
    plt.plot(ts_meas, Cg_meas, '.')
    plt.title("Glucose")

    plt.subplot(1, 3, 2)
    plt.plot(ts_meas, Cfa_meas, '.')
    plt.title("Fumaric")

    plt.subplot(1, 3, 3)
    plt.plot(ts_meas, Ce_meas, '.')
    plt.title("Ethanol")

    plt.savefig("results/data7.pdf")
    if show:
        plt.show()


# noinspection DuplicatedCode
def plot_model(file_name,  show=True):
    """Plots state update data and model data from a file

    Parameters
    ----------
    file_name : string
        The name of the file in which all the data is stored

    show : bool, optional
        If `True` then the plt.show method is called at the end.
        Useful to turn off when you want to add additional things
        Defaults to `True`
    """
    xls = pandas.ExcelFile(file_name)
    model = pandas.read_excel(xls, 'model')
    se = pandas.read_excel(xls, 'se')
    su = pandas.read_excel(xls, 'su')

    # Model
    ts_m = model['ts']
    Vs_m = model['V']
    Cgs_m = model['Ng'] * 180 / Vs_m
    Cfas_m = model['Nfa'] * 116 / Vs_m
    Ces_m = model['Ne'] * 46 / Vs_m
    Czs_m = model['Nz'] / Vs_m
    Cys_m = model['Ny'] / Vs_m
    Ts_m = model['T']
    pH_m = model['pH']

    # Measured update values
    ts_meas = su['ts']
    Cg_meas = su['Cg']
    Cfa_meas = su['Cfa']
    Ce_meas = su['Ce']

    plt.figure(figsize=(20, 20))
    plt.rc("font", size=20)
    plt.subplot(2, 2, 1)
    plt.plot(ts_m, Cgs_m, "--")
    plt.plot(ts_meas, Cg_meas, '.')
    plt.title("Glucose")

    plt.subplot(2, 2, 2)
    plt.plot(ts_m, Cfas_m, "--")
    plt.plot(ts_meas, Cfa_meas, '.')
    plt.title("Fumaric")

    plt.subplot(2, 2, 3)
    plt.plot(ts_m, Ces_m, "--")
    plt.plot(ts_meas, Ce_meas, '.')
    plt.title("Ethanol")

    plt.subplot(2, 2, 4)
    plt.plot(ts_m, Czs_m, "--", label="Z")

    plt.plot(ts_m, Cys_m, "--", label="Y")
    plt.title("Enzyme")
    plt.legend()

    plt.savefig("results/model7.pdf")
    if show:
        plt.show()


if __name__ == "__main__":
    plot_all('results/result.xlsx')
