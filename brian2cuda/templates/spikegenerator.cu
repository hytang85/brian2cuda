{% extends 'common_group.cu' %}
{% block extra_device_helper %}
int mem_per_thread(){
	return sizeof(int32_t);
}

__device__ unsigned int _last_element_checked = 0;
{% endblock %}

{% block kernel_call %}
kernel_{{codeobj_name}}<<<num_blocks, num_threads>>>(
		_N,
		num_threads,
		{{owner.clock.name}}.t[0],
		{{owner.clock.name}}.dt[0],
		///// HOST_PARAMETERS /////
		%HOST_PARAMETERS%
	);

cudaError_t status = cudaGetLastError();
if (status != cudaSuccess)
{
	printf("ERROR launching kernel_{{codeobj_name}} in %s:%d %s\n",
			__FILE__, __LINE__, cudaGetErrorString(status));
	_dealloc_arrays();
	exit(status);
}
{% endblock kernel_call %}


{% block kernel %}
    {# USES_VARIABLES {_spikespace, N, neuron_index, spike_time, period, _lastindex } #}

__global__ void kernel_{{codeobj_name}}(
	unsigned int _N,
	unsigned int THREADS_PER_BLOCK,
	double t,
	double dt,
	///// DEVICE_PARAMETERS /////
	%DEVICE_PARAMETERS%
	)
{
	{# USES_VARIABLES { N } #}
	using namespace brian;

	unsigned int tid = threadIdx.x;
	unsigned int bid = blockIdx.x;
	unsigned int _idx = bid * THREADS_PER_BLOCK + tid;
	unsigned int _vectorisation_idx = _idx;
	///// KERNEL_VARIABLES /////
	%KERNEL_VARIABLES%

	if(_idx >= _N)
	{
		return;
	}

    double _the_period = {{period}};
    double padding_before = fmod(t, _the_period);
    double padding_after  = fmod(t+dt, _the_period);
    double epsilon        = 1e-3*dt;

    // We need some precomputed values that will be used during looping
    bool not_first_spike = ({{_lastindex}} > 0);
    bool not_end_period  = (fabs(padding_after) > epsilon);
    bool test;
	
	//// MAIN CODE ////////////
	// scalar code
	
	for(int i = tid; i < N; i+= THREADS_PER_BLOCK)
	{
		{{_spikespace}}[i] = -1;
	}

	if(tid == 0)
	{
		//init number of spikes with 0
		{{_spikespace}}[N] = 0;
	}
	__syncthreads();

	for(int spike_idx = {{_lastindex}} + tid; spike_idx < _numspike_time; spike_idx += THREADS_PER_BLOCK)
	{
		if (not_end_period)
		{
	        test = ({{spike_time}}[spike_idx] > padding_after) || (fabs({{spike_time}}[spike_idx] - padding_after) < epsilon);
	    }
	    else
	    {
	        // If we are in the last timestep before the end of the period, we remove the first part of the
	        // test, because padding will be 0
	        test = (fabs({{spike_time}}[spike_idx] - padding_after) < epsilon);
	    }
	    if (test)
	    {
	        break;
	    }
	    int32_t neuron_id = {{neuron_index}}[spike_idx];
    	int32_t spikespace_index = atomicAdd(&{{_spikespace}}[N], 1);
		atomicAdd(&{{_lastindex}}, 1);
    	{{_spikespace}}[spikespace_index] = neuron_id;
		__syncthreads();
	}
}
{% endblock %}

{% block prepare_kernel_inner %}
num_threads = 1;
num_blocks = 1;
{% endblock %}
