'''
Check the speed of different Brian 2 configurations (with additional models for brian2cuda)
'''
from brian2 import *
from brian2.tests.features import SpeedTest
from brian2.tests.features.speed import *

from brian2.tests.features.speed import __all__
__all__.extend(['AdaptationOscillation',
                'BrunelHakimModelScalarDelay',
                'BrunelHakimModelHeterogeneousDelay',
                'COBAHH',
                'STDPEventDriven',
                'STDPNotEventDriven',
                'STDPMultiPost',
                'STDPNeuronalTraces',
                'STDPMultiPostNeuronalTraces',
                'Vogels',
                'VogelsWithSynapticDynamic'
               ])

        
class AdaptationOscillation(SpeedTest):
    
    category = "Full examples"
    name = "Adaptation oscillation"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        
        synapses = Synapses(neurons, neurons, 'c: volt', on_pre='v += c')
        synapses.connect('i!=j', p=sparsity)
        synapses.c[:] = 'syn_weight' 
        synapses.delay[:] = 'syn_delay' 
        
        self.timed_run(self.duration)

class BrunelHakimModelScalarDelay(SpeedTest):
    
    category = "Full examples"
    name = "Brunel Hakim with scalar delay"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        conn = Synapses(group, group, on_pre='V += -J', delay=delta)
        conn.connect('rand()<sparseness')
        
        self.timed_run(duration)
        
class BrunelHakimModelHeterogeneousDelay(SpeedTest):
    
    category = "Full examples"
    name = "Brunel Hakim with heterogenous delays"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        conn = Synapses(group, group, on_pre='V += -J')
        conn.connect('rand()<sparseness')
        conn.delay = "delta * 2 * rand()"
        
        self.timed_run(duration)

class COBAHH(SpeedTest):
    
    category = "Full examples"
    name = "COBAHH"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        Ce = Synapses(Pe, P, on_pre='ge+=we')
        Ce.connect('rand()<0.02')
        Ci = Synapses(Pi, P, on_pre='gi+=wi')
        Ci.connect('rand()<0.02')
        
        # Initialization
        P.v = 'El + (randn() * 5 - 5)*mV'
        P.ge = '(randn() * 1.5 + 4) * 10.*nS'
        P.gi = '(randn() * 12 + 20) * 10.*nS'
        
        self.timed_run(self.duration)

class STDPEventDriven(SpeedTest):
    
    category = "Full examples"
    name = "STDP (event-driven)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        
        input_poisson = PoissonGroup(N, rates=F)
        neurons = NeuronGroup(1, eqs_neurons, threshold='v>vt', reset='v = vr')
        S = Synapses(input_poisson, neurons,
                     '''w : 1
                        dApre/dt = -Apre / taupre : 1 (event-driven)
                        dApost/dt = -Apost / taupost : 1 (event-driven)''',
                     on_pre='''ge += w
                        Apre += dApre
                        w = clip(w + Apost, 0, gmax)''',
                     on_post='''Apost += dApost
                         w = clip(w + Apre, 0, gmax)'''
                    )
        S.connect()
        S.w = 'rand() * gmax'
        self.timed_run(self.duration)
        
class STDPNotEventDriven(SpeedTest):
    
    category = "Full examples"
    name = "STDP (not event-driven)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        
        input_poisson = PoissonGroup(N, rates=F)
        neurons = NeuronGroup(1, eqs_neurons, threshold='v>vt', reset='v = vr')
        S = Synapses(input_poisson, neurons,
                     '''w : 1
                        dApre/dt = -Apre / taupre : 1
                        dApost/dt = -Apost / taupost : 1''',
                     on_pre='''ge += w
                        Apre += dApre
                        w = clip(w + Apost, 0, gmax)''',
                     on_post='''Apost += dApost
                         w = clip(w + Apre, 0, gmax)''',
                     method=euler
                    )
        S.connect()
        S.w = 'rand() * gmax'
        self.timed_run(self.duration)
        

class STDPMultiPost(SpeedTest):
    '''
    Spike-timing dependent plasticity.
    Adapted from Song, Miller and Abbott (2000) and Song and Abbott (2001).

    This example is modified from ``synapses_STDP.py``.

    This version includes a further modification:
    multiple pre- _and_ postsynaptic neurons (s.t. no. synpases is N).
    '''

    category = "Full examples"
    name = "STDP with multiple pre- and postsynaptic neurons"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000, 1000000]#, 10000000]
    n_label = 'Num synapses'

    # configuration options
    duration = 1*second

    def run(self):
        N = self.n # no of synapses
        N_neuron = int(sqrt(N))
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

        input_poisson = PoissonGroup(N_neuron, rates=F)
        neurons = NeuronGroup(N_neuron, eqs_neurons, threshold='v>vt', reset='v = vr')
        S = Synapses(input_poisson, neurons,
                     '''w : 1
                        dApre/dt = -Apre / taupre : 1 (event-driven)
                        dApost/dt = -Apost / taupost : 1 (event-driven)''',
                     on_pre='''ge += w
                            Apre += dApre
                            w = clip(w + Apost, 0, gmax)''',
                     on_post='''Apost += dApost
                             w = clip(w + Apre, 0, gmax)''',
                     )
        S.connect()
        S.w = 'rand() * gmax'

        self.timed_run(self.duration)


class STDPNeuronalTraces(SpeedTest):
    '''
    Spike-timing dependent plasticity.
    Adapted from Song, Miller and Abbott (2000) and Song and Abbott (2001).

    This example is modified from ``synapses_STDP.py``.

    This version includes a further modification: traces in neurons.
    '''

    category = "Full examples"
    name = "STDP with traces in neurons"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000, 1000000]
    n_label = 'Num neurons (= num synapses)'

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

        input_poisson = NeuronGroup(N, '''rates : Hz
                                          dA/dt = -A / taupre : 1''',
                                    threshold='rand() < rates*dt')
        input_poisson.rates = F

        output_neuron = NeuronGroup(1, '''dv/dt = (ge * (Ee-vr) + El - v) / taum : volt
                                          dge/dt = -ge / taue : 1
                                          dA/dt = -A / taupost : 1''',
                                    threshold='v > vt', reset='v = vr; A += dApost')

        S = Synapses(input_poisson, output_neuron,
                     '''w : 1''',
                     on_pre='''ge += w
                            w = clip(w + A_post, 0, gmax)''',
                     on_post='''w = clip(w + A_pre, 0, gmax)''',
                     )
        S.connect()
        S.w = 'rand() * gmax'

        self.timed_run(self.duration)


class STDPMultiPostNeuronalTraces(SpeedTest):
    '''
    Spike-timing dependent plasticity.
    Adapted from Song, Miller and Abbott (2000) and Song and Abbott (2001).

    This example is modified from ``synapses_STDP.py``.

    This version includes two further modifications:
    traces in neurons and multiple pre- _and_ postsynaptic neurons (s.t. no. synpases is N).
    '''

    category = "Full examples"
    name = "STDP with multiple postsynaptic neurons and traces in neurons"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000, 1000000]
    n_label = 'Num synapses'

    # configuration options
    duration = 1*second

    def run(self):
        N = self.n
        N_neuron = int(sqrt(N))
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

        input_poissong = NeuronGroup(N_neuron, '''rates : Hz
                                                  dA/dt = -A / taupre : 1''',
                                     threshold='rand() < rates*dt')
        input_poissong.rates = F

        output_neuron = NeuronGroup(N_neuron, '''dv/dt = (ge * (Ee-vr) + El - v) / taum : volt
                                          dge/dt = -ge / taue : 1
                                          dA/dt = -A / taupost : 1''',
                                    threshold='v > vt', reset='v = vr; A += dApost')

        S = Synapses(input_poissong, output_neuron,
                     '''w : 1''',
                     on_pre='''ge += w
                            w = clip(w + A_post, 0, gmax)''',
                     on_post='''w = clip(w + A_pre, 0, gmax)''',
                     )
        S.connect()
        S.w = 'rand() * gmax'

        self.timed_run(self.duration)


class Vogels(SpeedTest):
    
    category = "Full examples"
    name = "Vogels et al 2011 (event-driven synapses)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        
        con_e = Synapses(Pe, neurons, on_pre='g_ampa += 0.3*nS')
        con_e.connect('rand()<epsilon')
        con_ii = Synapses(Pi, Pi, on_pre='g_gaba += 3*nS')
        con_ii.connect('rand()<epsilon')
        
        eqs_stdp_inhib = '''
        w : 1
        dA_pre/dt=-A_pre/tau_stdp : 1 (event-driven)
        dA_post/dt=-A_post/tau_stdp : 1 (event-driven)
        '''
        alpha = 3*Hz*tau_stdp*2  # Target rate parameter
        gmax = 100               # Maximum inhibitory weight
        
        con_ie = Synapses(Pi, Pe, model=eqs_stdp_inhib,
                          on_pre='''A_pre += 1.
                                 w = clip(w+(A_post-alpha)*eta, 0, gmax)
                                 g_gaba += w*nS''',
                          on_post='''A_post += 1.
                                  w = clip(w+A_pre*eta, 0, gmax)
                               '''
                         )
        con_ie.connect('rand()<epsilon')
        con_ie.w = 1e-10
        self.timed_run(self.duration)
        
class VogelsWithSynapticDynamic(SpeedTest):
    
    category = "Full examples"
    name = "Vogels et al 2011 (not event-driven synapses)"
    tags = ["Neurons", "Synapses"]
    n_range = [10, 100, 1000, 10000, 20000, 50000, 100000]
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
        
        con_e = Synapses(Pe, neurons, on_pre='g_ampa += 0.3*nS')
        con_e.connect('rand()<epsilon')
        con_ii = Synapses(Pi, Pi, on_pre='g_gaba += 3*nS')
        con_ii.connect('rand()<epsilon')
        
        eqs_stdp_inhib = '''
        w : 1
        dA_pre/dt=-A_pre/tau_stdp : 1
        dA_post/dt=-A_post/tau_stdp : 1
        '''
        alpha = 3*Hz*tau_stdp*2  # Target rate parameter
        gmax = 100               # Maximum inhibitory weight
        
        con_ie = Synapses(Pi, Pe, model=eqs_stdp_inhib,
                          on_pre='''A_pre += 1.
                                 w = clip(w+(A_post-alpha)*eta, 0, gmax)
                                 g_gaba += w*nS''',
                          on_post='''A_post += 1.
                                  w = clip(w+A_pre*eta, 0, gmax)
                               '''
                         )
        con_ie.connect('rand()<epsilon')
        con_ie.w = 1e-10
        self.timed_run(self.duration)
        
        



if __name__=='__main__':
    #prefs.codegen.target = 'numpy'
    VerySparseMediumRateSynapsesOnly(100000).run()
    show()
