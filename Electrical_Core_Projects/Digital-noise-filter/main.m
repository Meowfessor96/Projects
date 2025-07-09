
% To run the code without partial suppression leave the tonal_freqs empty
% And to run it with partial suppression enter the tonal frequencies at tonal_freqs


clc, clearvars

external_noise(:) = load('external_noise.txt');
noisy_speech(:) = load('noisy_speech.txt');
clean_speech(:) = load('clean_speech.txt');

N = min([numel(external_noise), numel(noisy_speech), numel(clean_speech)]);

external_noise = external_noise(1:N);
noisy_speech = noisy_speech(1:N);
clean_speech = clean_speech(1:N);

Fs = 44100;
filter_order = 2;
mu = 0.007;
epsilon = 1e-8;
tonal_freqs = [];

bandwidth = 10;
h = zeros(filter_order,1);
buffer = zeros(filter_order,1);
output = zeros(N,1);

notch_states = cell(length(tonal_freqs), 1);

for i = 1:length(tonal_freqs)
    notch_states{i} = zeros(2, 1);
end

for i = 1:N
    x_in = external_noise(i);
    
    % Applying notch filter if frequencies are specified
    if ~isempty(tonal_freqs)
        for j = 1:length(tonal_freqs)
            % Applying IIR notch filtering
            [x_in, notch_states{j}] = iir_notch_filter(x_in, notch_states{j}, Fs, tonal_freqs(j), bandwidth);
        end
    end
    
    if i < filter_order
        buffer = [x_in; buffer(1:end-1)];
        output(i) = noisy_speech(i);
    else
        buffer = [x_in; buffer(1:end-1)];
        y = h' * buffer;
        e = noisy_speech(i) - y;
        h = h + mu * e * buffer / (epsilon + (buffer' * buffer));
        output(i) = e;
    end
end

noise_before = noisy_speech - clean_speech;
noise_after = output' - clean_speech;

snr_before = 10*log10(sum(clean_speech.^2)/sum(noise_before.^2));
snr_after = 10*log10(sum(clean_speech.^2)/sum(noise_after.^2));

fprintf('SNR before: %.2f dB\n', snr_before);
fprintf('SNR after: %.2f dB\n', snr_after);
fprintf('Improvement: %.2f dB\n', snr_after - snr_before);

audiowrite('enhanced_speech.wav', output./max(abs(output)), Fs);

% IIR notch filter of order 2
function [y, states] = iir_notch_filter(x, states, Fs, f0, bandwidth)
    omega0 = 2 * pi * f0 / Fs;
    BW = 2 * pi * bandwidth / Fs;
    r = 1 - BW/2; 
    
    b = [1, -2*cos(omega0), 1];  
    a = [1, -2*r*cos(omega0), r^2];  

    w0 = x - a(2)*states(1) - a(3)*states(2);
    y = b(1)*w0 + b(2)*states(1) + b(3)*states(2);

    states = [w0; states(1)];
end