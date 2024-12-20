# For the training we use the functions with the relaxation/retardation time as parameter. This helps to avoid numerical instabilities.

# Import required packages
import numpy as np
import math
from scipy.special import gamma

# Import Mittag-Leffler implementations from their .py files
from pyRheo.mittag_leffler.ml_pade32 import R_alpha_beta_3_2
from pyRheo.mittag_leffler.ml_pade54 import R_alpha_beta_5_4
from pyRheo.mittag_leffler.ml_pade63 import R_alpha_beta_6_3
from pyRheo.mittag_leffler.ml_pade72 import R_alpha_beta_7_2
from pyRheo.mittag_leffler.ml_garrappa import E_alpha_beta

# Error function
def createRandomError(n, std):
    return np.random.normal(loc=(1), scale=(std), size=(n,))
    

# Relaxation models

# Maxwell model
def MaxwellModel(G_s, tau_c, t, errorInserted=0):
    """
    Compute the Maxwell model response

    Parameters
    ----------
    G_s : float
        Shear modulus (Pa). Subindex "s" implies that the element is connected in serie.
    eta_s : float
        Viscosity (Pa s). Subindex "s" implies that the element is connected in serie.
    t : numpy
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`.
    """ 
    #tau_c = eta_s / G_s
    result = G_s * np.exp(np.divide(-t, tau_c))
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result,error)
        
    return result

# SpringPot model
def SpringPot(V, alpha, t, errorInserted=0):
    """
    Compute the SpringPot model response

    Parameters
    ----------
    V: float.
       Quasi-modulus (Pa*s^alpha)
    alpha: float 
        Parameter between [0, 1] (dimensionless).
    t : numpy
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`.
    """ 
    result = V * (np.divide(np.power(t, -alpha), gamma(1 - alpha)))
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result,error)
        
    return result

# Fractional Maxwell Gel model (springpot-spring)
def FractionalMaxwellGel(V, G_s, alpha, t, errorInserted=0, mittag_leffler_type="Pade63"):
    """
    Compute the Fractional Maxwell Gel model response

    Parameters
    ----------
    V : float
        Quasi-modulus (Pa*s^alpha).
    G_s : float
        Shear modulus (Pa). Subindex "s" implies that the element is connected in serie.
    alpha : float
        Fractional order parameter between 0 and 1 (dimensionless).
    t : numpy.ndarray
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).
    mittag_leffler_type : str, optional
        Type of function to use ("Pade" or "Garrappa")
        
    Returns
    -------
    result : ndarray
        The relaxation modulus response at each time point in `t`.
    """
    tau_c = (V / G_s)**(1 / alpha)
    G_c = V * tau_c**(-alpha)
    z = -np.power(np.divide(t, tau_c), alpha)
    
    if mittag_leffler_type == "Pade32":
        response_func = R_alpha_beta_3_2
    elif mittag_leffler_type == "Pade54":
        response_func = R_alpha_beta_5_4
    elif mittag_leffler_type == "Pade63":
        response_func = R_alpha_beta_6_3
    elif mittag_leffler_type == "Pade72":
        response_func = R_alpha_beta_7_2
    elif mittag_leffler_type == "Garrappa":
        response_func = E_alpha_beta
    else:
        raise ValueError("mittag_leffler_type must be either 'Pade' or 'Garrappa'")
    
    result = np.multiply(G_c, response_func(z, alpha, 1))
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result, error)
        
    return result


# Fractional Maxwell Liquid model (springpot-dashpot)
def FractionalMaxwellLiquid(G, eta_s, beta, t, errorInserted=0, mittag_leffler_type="Pade63"):
    """
    Compute the Fractional Maxwell Liquid model response

    Parameters
    ----------
    G : float
        Quasi-modulus (Pa*s^beta).
    eta_s: float.
        viscosity (Pa*s). Subindex "s" implies that the element is connected in serie.
    beta : float
        Fractional order parameter between 0 and 1 (dimensionless).
    t : numpy.ndarray
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).
    mittag_leffler_type : str, optional
        Type of function to use ("Pade" or "Garrappa")
        
    Returns
    -------
    result : ndarray
        The relaxation modulus response at each time point in `t`.
    """
    tau_c = (eta_s / G)**(1 / (1 - beta))
    G_c = eta_s * tau_c**(-1)
    z = -np.power(np.divide(t, tau_c), (1 - beta))
    a = 1 - beta
    b = 1 - beta + 1e-16
    
    if mittag_leffler_type == "Pade32":
        response_func = R_alpha_beta_3_2
    elif mittag_leffler_type == "Pade54":
        response_func = R_alpha_beta_5_4
    elif mittag_leffler_type == "Pade63":
        response_func = R_alpha_beta_6_3
    elif mittag_leffler_type == "Pade72":
        response_func = R_alpha_beta_7_2
    elif mittag_leffler_type == "Garrappa":
        response_func = E_alpha_beta
    else:
        raise ValueError("mittag_leffler_type must be either 'Pade' or 'Garrappa'")
    
    result = G_c * np.multiply(np.power(np.divide(t, tau_c), -beta), response_func(z, a, b))
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result, error)
        
    return result

# Fractional Maxwell model (springpot-springpot)
def FractionalMaxwellModel(tau_c, V, alpha, beta, t, errorInserted=0, mittag_leffler_type="Pade63"):
    """
    Compute the Fractional Maxwell model response

    Parameters
    ----------
    G: float.
        Quasi-modulus (Pa*s^beta)
    V: float.
        Quasi-modulus (Pa*s^alpha)
    alpha: float 
        Parameter between [0, 1] (dimensionless).
    beta: float 
        Parameter between [0, 1] (dimensionless).
    t : numpy
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).
    mittag_leffler_type : str, optional
        Type of function to use ("Pade" or "Garrappa")

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`.
    """
    #tau_c = (V / G)**(1 / (alpha - beta))
    G_c = V * (tau_c**(-alpha))
    z = -np.power(np.divide(t, tau_c), alpha - beta)
    a = alpha - beta
    b = 1 - beta
    
    if mittag_leffler_type == "Pade32":
        response_func = R_alpha_beta_3_2
    elif mittag_leffler_type == "Pade54":
        response_func = R_alpha_beta_5_4
    elif mittag_leffler_type == "Pade63":
        response_func = R_alpha_beta_6_3
    elif mittag_leffler_type == "Pade72":
        response_func = R_alpha_beta_7_2
    elif mittag_leffler_type == "Garrappa":
        response_func = E_alpha_beta
    else:
        raise ValueError("mittag_leffler_type must be either 'Pade' or 'Garrappa'")
    
    result = G_c * np.multiply(np.power(np.divide(t, tau_c), -beta), response_func(z, a, b))
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result, error)
        
    return result
 
# Fractional Kelvin-Voigt model (spring-springpot)
def FractionalKelvinVoigtS(G_p, V, alpha, t, errorInserted=0):
    """
    Compute the Fractional Kelvin-VoigtS model response

    Parameters
    ----------
    G_p: float.
        shear modulus (Pa). Subindex "p" implies that the element is connected in parallel.
    V: float
        Quasi-modulus (Pa*s^alpha)
    alpha: float 
        Parameter between [0, 1] (dimensionless).
    t: numpy.ndarray
        Array of time values (s).
    errorInserted: float, optional
        Optional error to insert into the model (default is 0).

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`.
    """
    term1 = V * np.divide(np.power(t, -alpha), gamma(1 - alpha))  
    result = term1 + G_p  

    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result,error)
        
    return result 
    
# Fractional Kelvin-Voigt model (springpot-dashpot) 
def FractionalKelvinVoigtD(G, eta_p, beta, t, errorInserted=0):
    """
    Compute the Fractional Kelvin-VoigtD model response

    Parameters
    ----------
    G: float
        Quasi-modulus (Pa*s^beta)
    eta: float
        Viscosity (Pa*s)
    beta: float 
        Parameter between [0, 1] (dimensionless).
    t: numpy.ndarray
        Array of time values (s).
    errorInserted: float, optional
        Optional error to insert into the model (default is 0).

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`
    """
    positive_infinity = math.inf    
    dirac_term = np.where(t == 0, positive_infinity, 0.0)  # Dirac delta approximation
    term1 = eta_p * dirac_term  
    term2 = G * np.divide(np.power(t, -beta), gamma(1 - beta))  
    result = term1 + term2

    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result,error)
        
    return result

# Fractional Kelvin-Voigt model (springpot-springpot)
def FractionalKelvinVoigtModel(G, V, alpha, beta, t, errorInserted=0):
    """
    Compute the Fractional Kelvin-Voigt model response for given quasi-moduli, fractional orders, 
    and time array with optional error insertion.

    Parameters
    ----------
    G: float.
        Quasi-modulus (Pa*s^beta)
    V: float.
        Quasi-modulus (Pa*s^alpha)
    alpha: float 
        Parameter between [0, 1] (dimensionless).
    beta: float 
        Parameter between [0, 1] (dimensionless).
    t : numpy
        Array of time values (s).
    errorInserted : float, optional
        Optional error to insert into the model (default is 0).

    Returns
    -------
    ndarray
        The stress relaxation response at each time point in `t`.
    """
    term1 = V * np.divide(np.power(t, -alpha), gamma(1 - alpha))
    term2 = G * np.divide(np.power(t, -beta), gamma(1 - beta))
    result = np.add(term1, term2)
    
    if errorInserted != 0:
        error = createRandomError(t.shape[0], errorInserted)
        result = np.multiply(result, error)
        
    return result

