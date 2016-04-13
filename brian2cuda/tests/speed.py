'''
Check the speed of different Brian 2 configurations (with additional models for brian2cuda)
'''
from brian2 import *
from brian2.tests.features import SpeedTest
from brian2.tests.features.speed import *

from brian2.tests.features.speed import __all__
__all__.extend(['AdaptationOscillation',
                'BrunelHakimModel',
                'BrunelHakimModelWithDelay',
                'COBAHH',
                'STDPEventDriven',
                'STDPNotEventDriven',
                'Vogels',
                'VogelsWithSynapticDynamic'
               ])

        
class AdaptationOscillation(SpeedTest):
    
    category = "Full examples"
    name = "Adaptation oscillation"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N_neurons = self.n
        sparsity = 0.05 # each neuron receives approx. N_neurons*sparsity connections => 0: uncoupled network
        tau_v = 10 * ms # membrane time const
        tau_w = 200 * ms # adaptation time const
        v_t = 1 * mV # threshold voltage
        v_r = 0 * mV # reset voltage
        dw = 0.1 * mV # spike-triggered adaptation increment
        Tref = 2.5 * ms # refractory period
        syn_weight = 1.03/(N_neurons*sparsity) * mV # currently: constant synaptic weights
        syn_delay = 2 * ms
        # input noise:
        input_mean = 0.14 * mV/ms
        input_std = 0.07 * mV/ms**.5
        
        # brian neuron model specification
        eqs_neurons = '''
        dv/dt = (-v-w)/tau_v + input_mean + input_std*xi : volt (unless refractory)
        dw/dt = -w/tau_w : volt (unless refractory)
        '''
        reset_neurons = '''
        v = v_r
        w = w+dw
        '''
        
        neurons = NeuronGroup(N_neurons, 
                              eqs_neurons, 
                              reset=reset_neurons,
                              threshold='v > v_t', 
                              refractory='Tref')
        
        # random initialization of neuron state values
        neurons.v = 'rand()*v_t' 
        neurons.w = 'rand()*10*dw'
        
        synapses = Synapses(neurons, neurons, 'c: volt', pre='v += c')
        synapses.connect('i!=j', p=sparsity)
        synapses.c[:] = 'syn_weight' 
        synapses.delay[:] = 'syn_delay' 
        
        run(self.duration, report="text")

class BrunelHakimModel(SpeedTest):
    
    category = "Full examples"
    name = "Brunel Hakim "
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        Vr = 10*mV
        theta = 20*mV
        tau = 20*ms
        delta = 2*ms
        taurefr = 2*ms
        duration = .1*second
        C = 1000
        sparseness = float(C)/N
        J = .1*mV
        muext = 25*mV
        sigmaext = 1*mV
        
        eqs = """
        dV/dt = (-V+muext + sigmaext * sqrt(tau) * xi)/tau : volt
        """
        
        group = NeuronGroup(N, eqs, threshold='V>theta',
                            reset='V=Vr', refractory=taurefr)
        group.V = Vr
        conn = Synapses(group, group, pre='V += -J',
                        connect='rand()<sparseness')
        conn.delay = delta
        
        run(duration, report="text")
        
class BrunelHakimModelWithDelay(SpeedTest):
    
    category = "Full examples"
    name = "Brunel Hakim "
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        Vr = 10*mV
        theta = 20*mV
        tau = 20*ms
        delta = 2*ms
        taurefr = 2*ms
        duration = .1*second
        C = 1000
        sparseness = float(C)/N
        J = .1*mV
        muext = 25*mV
        sigmaext = 1*mV
        
        eqs = """
        dV/dt = (-V+muext + sigmaext * sqrt(tau) * xi)/tau : volt
        """
        
        group = NeuronGroup(N, eqs, threshold='V>theta',
                            reset='V=Vr', refractory=taurefr)
        group.V = Vr
        conn = Synapses(group, group, pre='V += -J',
                        connect='rand()<sparseness')
        conn.delay = "delta * 2 * rand()"
        
        run(duration, report="text")

class COBAHH(SpeedTest):
    
    category = "Full examples"
    name = "COBAHH"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        area = 20000*umetre**2
        Cm = (1*ufarad*cm**-2) * area
        gl = (5e-5*siemens*cm**-2) * area
        
        El = -60*mV
        EK = -90*mV
        ENa = 50*mV
        g_na = (100*msiemens*cm**-2) * area
        g_kd = (30*msiemens*cm**-2) * area
        VT = -63*mV
        # Time constants
        taue = 5*ms
        taui = 10*ms
        # Reversal potentials
        Ee = 0*mV
        Ei = -80*mV
        we = 6*nS  # excitatory synaptic weight
        wi = 67*nS  # inhibitory synaptic weight
        
        # The model
        eqs = Equations('''
        dv/dt = (gl*(El-v)+ge*(Ee-v)+gi*(Ei-v)-
                 g_na*(m*m*m)*h*(v-ENa)-
                 g_kd*(n*n*n*n)*(v-EK))/Cm : volt
        dm/dt = alpha_m*(1-m)-beta_m*m : 1
        dn/dt = alpha_n*(1-n)-beta_n*n : 1
        dh/dt = alpha_h*(1-h)-beta_h*h : 1
        dge/dt = -ge*(1./taue) : siemens
        dgi/dt = -gi*(1./taui) : siemens
        alpha_m = 0.32*(mV**-1)*(13*mV-v+VT)/
                 (exp((13*mV-v+VT)/(4*mV))-1.)/ms : Hz
        beta_m = 0.28*(mV**-1)*(v-VT-40*mV)/
                (exp((v-VT-40*mV)/(5*mV))-1)/ms : Hz
        alpha_h = 0.128*exp((17*mV-v+VT)/(18*mV))/ms : Hz
        beta_h = 4./(1+exp((40*mV-v+VT)/(5*mV)))/ms : Hz
        alpha_n = 0.032*(mV**-1)*(15*mV-v+VT)/
                 (exp((15*mV-v+VT)/(5*mV))-1.)/ms : Hz
        beta_n = .5*exp((10*mV-v+VT)/(40*mV))/ms : Hz
        ''')
        
        P = NeuronGroup(N, model=eqs, threshold='v>-20*mV', refractory=3*ms,
                        method='exponential_euler')
        N_Pi = int(0.8*N)
        Pe = P[:N_Pi]
        Pi = P[N_Pi:]
        Ce = Synapses(Pe, P, pre='ge+=we', connect='rand()<0.02')
        Ci = Synapses(Pi, P, pre='gi+=wi', connect='rand()<0.02')
        
        # Initialization
        P.v = 'El + (randn() * 5 - 5)*mV'
        P.ge = '(randn() * 1.5 + 4) * 10.*nS'
        P.gi = '(randn() * 12 + 20) * 10.*nS'
        
        run(self.duration, report="text")

class STDPEventDriven(SpeedTest):
    
    category = "Full examples"
    name = "STDP (event-driven)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        taum = 10*ms
        taupre = 20*ms
        taupost = taupre
        Ee = 0*mV
        vt = -54*mV
        vr = -60*mV
        El = -74*mV
        taue = 5*ms
        F = 15*Hz
        gmax = .01
        dApre = .01
        dApost = -dApre * taupre / taupost * 1.05
        dApost *= gmax
        dApre *= gmax
    
        eqs_neurons = '''
        dv/dt = (ge * (Ee-vr) + El - v) / taum : volt
        dge/dt = -ge / taue : 1
        '''
        
        input = PoissonGroup(N, rates=F)
        neurons = NeuronGroup(1, eqs_neurons, threshold='v>vt', reset='v = vr')
        S = Synapses(input, neurons,
                     '''w : 1
                        dApre/dt = -Apre / taupre : 1 (event-driven)
                        dApost/dt = -Apost / taupost : 1 (event-driven)''',
                        pre='''ge += w
                        Apre += dApre
                        w = clip(w + Apost, 0, gmax)''',
                    post='''Apost += dApost
                         w = clip(w + Apre, 0, gmax)''',
                    connect=True
                    )
        S.w = 'rand() * gmax'
        run(self.duration, report="text")
        
class STDPNotEventDriven(SpeedTest):
    
    category = "Full examples"
    name = "STDP (not event-driven)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        taum = 10*ms
        taupre = 20*ms
        taupost = taupre
        Ee = 0*mV
        vt = -54*mV
        vr = -60*mV
        El = -74*mV
        taue = 5*ms
        F = 15*Hz
        gmax = .01
        dApre = .01
        dApost = -dApre * taupre / taupost * 1.05
        dApost *= gmax
        dApre *= gmax
    
        eqs_neurons = '''
        dv/dt = (ge * (Ee-vr) + El - v) / taum : volt
        dge/dt = -ge / taue : 1
        '''
        
        input = PoissonGroup(N, rates=F)
        neurons = NeuronGroup(1, eqs_neurons, threshold='v>vt', reset='v = vr')
        S = Synapses(input, neurons,
                     '''w : 1
                        dApre/dt = -Apre / taupre : 1
                        dApost/dt = -Apost / taupost : 1''',
                        pre='''ge += w
                        Apre += dApre
                        w = clip(w + Apost, 0, gmax)''',
                    post='''Apost += dApost
                         w = clip(w + Apre, 0, gmax)''',
                    connect=True,
                    method=euler
                    )
        S.w = 'rand() * gmax'
        run(self.duration, report="text")
        
class Vogels(SpeedTest):
    
    category = "Full examples"
    name = "Vogels et al 2011 (event-driven synapses)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        NE = int(0.8 * N)           # Number of excitatory cells
        NI = NE/4          # Number of inhibitory cells 
        tau_ampa = 5.0*ms   # Glutamatergic synaptic time constant
        tau_gaba = 10.0*ms  # GABAergic synaptic time constant
        epsilon = 0.02      # Sparseness of synaptic connections
        tau_stdp = 20*ms    # STDP time constant
        gl = 10.0*nsiemens   # Leak conductance
        el = -60*mV          # Resting potential
        er = -80*mV          # Inhibitory reversal potential
        vt = -50.*mV         # Spiking threshold
        memc = 200.0*pfarad  # Membrane capacitance
        bgcurrent = 200*pA   # External current
        eta = 0
        
        eqs_neurons='''
        dv/dt=(-gl*(v-el)-(g_ampa*v+g_gaba*(v-er))+bgcurrent)/memc : volt (unless refractory)
        dg_ampa/dt = -g_ampa/tau_ampa : siemens
        dg_gaba/dt = -g_gaba/tau_gaba : siemens
        '''
        
        neurons = NeuronGroup(NE+NI, model=eqs_neurons, threshold='v > vt',
                              reset='v=el', refractory=5*ms)
        Pe = neurons[:NE]
        Pi = neurons[NE:]
        
        con_e = Synapses(Pe, neurons, pre='g_ampa += 0.3*nS', connect='rand()<epsilon')
        con_ii = Synapses(Pi, Pi, pre='g_gaba += 3*nS', connect='rand()<epsilon')
        
        eqs_stdp_inhib = '''
        w : 1
        dA_pre/dt=-A_pre/tau_stdp : 1 (event-driven)
        dA_post/dt=-A_post/tau_stdp : 1 (event-driven)
        '''
        alpha = 3*Hz*tau_stdp*2  # Target rate parameter
        gmax = 100               # Maximum inhibitory weight
        
        con_ie = Synapses(Pi, Pe, model=eqs_stdp_inhib,
                          pre='''A_pre += 1.
                                 w = clip(w+(A_post-alpha)*eta, 0, gmax)
                                 g_gaba += w*nS''',
                          post='''A_post += 1.
                                  w = clip(w+A_pre*eta, 0, gmax)
                               ''',
                          connect='rand()<epsilon')
        con_ie.w = 1e-10
        run(self.duration, report="text")
        
class VogelsWithSynapticDynamic(SpeedTest):
    
    category = "Full examples"
    name = "Vogels et al 2011 (not event-driven synapses)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 100000, 20000, 50000, 100000]
    n_label = 'Num neurons'

    # configuration options
    duration = 1*second
    
    def run(self):
        N = self.n
        NE = int(0.8 * N)           # Number of excitatory cells
        NI = NE/4          # Number of inhibitory cells 
        tau_ampa = 5.0*ms   # Glutamatergic synaptic time constant
        tau_gaba = 10.0*ms  # GABAergic synaptic time constant
        epsilon = 0.02      # Sparseness of synaptic connections
        tau_stdp = 20*ms    # STDP time constant
        gl = 10.0*nsiemens   # Leak conductance
        el = -60*mV          # Resting potential
        er = -80*mV          # Inhibitory reversal potential
        vt = -50.*mV         # Spiking threshold
        memc = 200.0*pfarad  # Membrane capacitance
        bgcurrent = 200*pA   # External current
        eta = 0
        
        eqs_neurons='''
        dv/dt=(-gl*(v-el)-(g_ampa*v+g_gaba*(v-er))+bgcurrent)/memc : volt (unless refractory)
        dg_ampa/dt = -g_ampa/tau_ampa : siemens
        dg_gaba/dt = -g_gaba/tau_gaba : siemens
        '''
        
        neurons = NeuronGroup(NE+NI, model=eqs_neurons, threshold='v > vt',
                              reset='v=el', refractory=5*ms)
        Pe = neurons[:NE]
        Pi = neurons[NE:]
        
        con_e = Synapses(Pe, neurons, pre='g_ampa += 0.3*nS', connect='rand()<epsilon')
        con_ii = Synapses(Pi, Pi, pre='g_gaba += 3*nS', connect='rand()<epsilon')
        
        eqs_stdp_inhib = '''
        w : 1
        dA_pre/dt=-A_pre/tau_stdp : 1
        dA_post/dt=-A_post/tau_stdp : 1
        '''
        alpha = 3*Hz*tau_stdp*2  # Target rate parameter
        gmax = 100               # Maximum inhibitory weight
        
        con_ie = Synapses(Pi, Pe, model=eqs_stdp_inhib,
                          pre='''A_pre += 1.
                                 w = clip(w+(A_post-alpha)*eta, 0, gmax)
                                 g_gaba += w*nS''',
                          post='''A_post += 1.
                                  w = clip(w+A_pre*eta, 0, gmax)
                               ''',
                          connect='rand()<epsilon')
        con_ie.w = 1e-10
        run(self.duration, report="text")
        
        



if __name__=='__main__':
    #prefs.codegen.target = 'numpy'
    VerySparseMediumRateSynapsesOnly(100000).run()
    show()
