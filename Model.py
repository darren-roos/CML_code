# Contains code for the system model
import numpy


class Model:
    """A nonlinear model of the system

    Parameters
    ----------
    X0 : array_like
        Initial states

    inputs : callable
        Must take in a parameter t (the current time) and return an array_like of the current inputs

    t : float, optional
        Initial time.
        Defaults to zero

    pH_calculations : bool, optional
        If `True` then pH calculations are made.
        Defaults to `False`

    Attributes
    -----------
    X : array_like
        Array of current state

    inputs : callable
        Must take in a parameter t (the current time) and return an array_like of the current inputs

    t : float
        Initial time

    pH_calculations : bool
        If `True` then pH calculations are made

    rate_matrix_inv : 2d array_like
        The inverse of the rate matrix.
        Placed here so that it is only calculated once
    """
    def __init__(self, X0, inputs, t=0, pH_calculations=False):
        self.X = numpy.array(X0)
        self.inputs = inputs
        self.t = t
        self.pH_calculations = pH_calculations

        self._Xs = [self.outputs()]

        alpha, PO, gamma, theta, beta = 0.1, 0.1, 1.8, 0.1, 0.1
        rate_matrix = numpy.array([[1, 0, 0, 0, 0],
                                   [0, 0, 0, 1, 0],
                                   [0, 0, 0, 0, 1],
                                   [-6, 4, 7/3, 2, -gamma],
                                   [0, 12, -1, 0, beta]])
        self.rate_matrix_inv = numpy.linalg.inv(rate_matrix)

    def DEs(self, t):
        """Contains the differential and algebraic equations for the system model.
        The rate equations defined in the matrix `rate_matrix` are described by: \n
        1) glucose + 2*CO2 + 6*ATP --> 2*FA + 2*water
        2) glucose --> 6*CO2 + 12*NADH + 4*ATP (TCA)
        3) NADH + 0.5*O2 -> 7/3 ATP (Respiration)
        4) glucose -> 2*ethanol + 2*CO2 + 2*ATP
        5) glucose + gamma*ATP --> 6*biomass + beta*NADH

        where the unknowns are: rFAp, rTCA, rResp, rEp, rXp

        Parameters
        ----------
        t : float
            The current time

        Returns
        -------
        dX : array_like
            The differential changes to the state variables
        """
        Ng, Nx, Nfa, Ne, Nco, No, Nn, Na, Nb, Nz, Ny, V, Vg, T = [max(0, N) for N in self.X]
        Fg_in, Cg_in, Fco_in, Cco_in, Fo_in, Co_in, \
            Fg_out, Cn_in, Fn_in, Fb_in, Cb_in, Fm_in, Fout, Tamb, Q = self.inputs(t)

        alpha, PO, gamma, theta, beta = 0.1, 0.1, 1.8, 0.1, 0.1
        delta = 0.2

        # Concentrations
        Cg, Cx, Cfa, Ce, Cn, Ca, Cb, Cz, Cy = [N/V for N in [Ng, Nx, Nfa, Ne, Nn, Na, Nb, Nz, Ny]]
        Cco, Co = [N/Vg for N in [Nco, No]]

        first_increase = (0.6 / 46 / 25 * 4) * Cy * 1.8
        second_increase = 2/46/120*3.2
        decrease = (0.6 / 46 / 40*3) * Cz/3
        rZ = decrease + second_increase if Cz > 0 else 0  # decrease
        rY = first_increase + decrease if Cy > 0 else 0  # increase

        rFAf = 15e-3 * (Cg / (1e-2 + Cg)) - 0.5 * rZ
        rEf = (second_increase + rY) * (Cg / (1e-5 + Cg))
        theta_calc = theta * (Cg / (1e-3 + Cg))
        RHS = [rFAf, rEf, 8e-5, theta_calc, 0]

        rFAf, rTCA, rResp, rEf, rbio = self.rate_matrix_inv @ RHS

        rG = -rFAf - rTCA - rEf - rbio
        rX = 6 * rbio
        rFA = 2*(rFAf + 0.5 * rZ)
        rE = 2 * (rEf - rZ) * (Cg / (1e-5 + Cg))
        rCO = -2 * rFAf + 6 * rTCA + 2 * rEf + alpha * rbio
        rO = -0.5*rResp

        # DE's
        dNg = Fg_in*Cg_in - Fout*Cg + rG*Cx*V
        dNx = rX*Cx*V
        dNfa = -Fout*Cfa + rFA*Cx*V
        dNe = -Fout*Ce + rE*Cx*V
        dNco = Fco_in*Cco_in - Fg_out*Cco + rCO*Cx*V
        dNo = Fo_in*Co_in - Fg_out*Co - rO*Cx*V
        dNn = Fn_in*Cn_in - Fout*Cn - delta*rX*Cx*V
        dNa = - Fout * Ca
        dNb = Fb_in*Cb_in - Fout*Cb
        dNz = -190*rZ*Cx*V
        dNy = -95*rY*Cx*V
        dV = Fg_in + Fn_in + Fb_in + Fm_in - Fout
        dVg = Fco_in + Fo_in - Fg_out
        dT = 4.5*Q - 0.25*(T - Tamb)

        return dNg, dNx, dNfa, dNe, dNco, dNo, dNn, dNa, dNb, dNz, dNy, dV, dVg, dT

    def step(self, dt):
        """Updates the model with inputs

        Parameters
        ----------
        dt : float
            Time since previous step

        """
        self.t += dt
        dX = self.DEs(self.t)
        self.X += numpy.array(dX)*dt
        self._Xs.append(self.outputs())

    def calculate_pH(self):
        """Calculates the pH in the vessel.

        Returns
        -------
        pH : float
            The pH of the tank
        """
        K_fa1, K_fa2,  K_a, K_b, K_w = 10 ** (-3.03), 10 ** 4.44, 10 ** 8.08, 10 ** 0.56, 10 ** (-14)
        _, _, Nfa, _, _, _, _, Na, Nb, _, _, V, _, _ = self.X
        C_fa = Nfa/V
        C_a = Na/V
        C_b = Nb/V

        def charge_balance(pH_guess):
            Ch = 10 ** (-pH_guess)
            C_fa_minus = K_fa1 * C_fa / (K_fa1 + Ch)
            C_fa_minus2 = K_fa2 * C_fa_minus / (K_fa2 + Ch)
            C_cl_minus = K_a * C_a / (K_a + Ch)
            C_oh_minus = K_w / Ch
            C_na_plus = K_b * C_b / (K_b + C_oh_minus)

            balance = Ch + C_na_plus - C_fa_minus - C_fa_minus2 - C_cl_minus - C_oh_minus
            return balance

        pHs = numpy.linspace(0, 14, 100)
        CBs = charge_balance(pHs)
        index = numpy.argmin(abs(CBs))
        pH = pHs[index]
        if abs(CBs[index]) > 1e-1:
            print('ph CB:', CBs[index])

        return pH

    def outputs(self):
        """Returns all the outputs (state and calculated)

        Returns
        -------
        outputs : array_like
            List of all the outputs from the model
        """
        if self.pH_calculations:
            pH = self.calculate_pH()
            outs = numpy.append(self.X, pH)
        else:
            outs = self.X
        return outs

    def get_Xs(self):
        """Gets all the states that are stored"""
        return numpy.array(self._Xs)

    def get_data(self):
        """Gets all relevant information from the object """
        return self.get_Xs()
