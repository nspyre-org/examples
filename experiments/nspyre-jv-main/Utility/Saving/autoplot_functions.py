import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import json
import os

def load_dataset(filename):

    f = open(filename)
    dataset = json.load(f)
    f.close()

    dataset_name = os.path.basename(filename).partition('.')[0]

    return dataset, dataset_name

def autoplot_sweep1d(filename, save_figure=True, show_figure=False):
    # load data
    dataset, dataset_name = load_dataset(filename)

    # plot
    x = dataset['x']
    z0 = dataset['z_ch0']
    plt.plot(x,z0,'-o',label='ch0')

    # plot data from 2nd channel, if enabled
    try:
        if dataset['params']['diff_onoff'] == 1:
            z1 = dataset['z_ch1']
            plt.plot(x,z1,'-o',label='ch1')
            plt.legend()
    except:
        pass

    plt.grid()
    plt.xlabel(dataset['x_label'])
    plt.ylabel(dataset['z_label'])
    plt.title(dataset_name)

    # save
    if save_figure:
        plt.savefig(filename.replace('.json','.png'))

    # pop up
    if show_figure:
        plt.show()

def autoplot_sweep2d(filename, save_figure=True, show_figure=False):
    # load data
    dataset, dataset_name = load_dataset(filename)

    # process data:
    x = dataset['x']
    y = dataset['y']
    z0 = dataset['z_ch0_arr']

    try:
        z1 = dataset['z_ch1_arr']
    except:
        z1 = 0*z0

    # plot
    try:
        if dataset['params']['diff_onoff'] == 1:
            z = np.array(z0) - np.array(z1)
            plt.pcolormesh(x,y,np.transpose(z))
            plt.legend()
        else:
            plt.pcolormesh(x,y,np.transpose(z0))
    except:
        plt.pcolormesh(x,y,np.transpose(z0))
    plt.grid(linestyle='--')
    plt.xlabel(dataset['x_label'])
    plt.ylabel(dataset['y_label'])

    colorbar_label = dataset['z_label']
    cbar = plt.colorbar()
    cbar.set_label(colorbar_label,rotation=270)

    plt.title(dataset_name)

    # save
    if save_figure:
        plt.savefig(filename.replace('.json','.png'))

    # pop up
    if show_figure:
        plt.show()

def autoplot_spectrum1d(filename, save_figure=True, show_figure=False):
    # load data
    dataset, dataset_name = load_dataset(filename)

    # process data:
    x = dataset['x']
    y = dataset['y']

    # plot
    plt.plot(x,y,'-')
    plt.grid()
    plt.xlabel(dataset['params']['x_label'])
    plt.ylabel(dataset['params']['y_label'])
    plt.title(dataset_name)

    # save
    if save_figure:
        plt.savefig(filename.replace('.json','.png'))

    # pop up
    if show_figure:
        plt.show()

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

# contout line plot
def plot_colourline(x,y,c,c_min,c_max, **xargs):
    # c = cm.viridis((c-np.min(c))/(np.max(c)-np.min(c)))
    c = cm.viridis((c-c_min)/(c_max-c_min))
    ax = plt.gca()
    for idx in np.arange(len(x)-1):
        ax.plot([x[idx],x[idx+1]], [y[idx],y[idx+1]], c=c[idx], **xargs)
    return

def autoplot_scan2d_pcolormesh(filename, save_figure=True):

    # load sweep
    f = open(filename)
    dataset = json.load(f)
    f.close()

    # name of dataset, to be used as plot title
    dataset_name = os.path.basename(filename).partition('.')[0]

    # path and name to save image
    filename_png = filename.replace('.json','.png')

    # process sweep
    x = np.array(dataset['x'])
    y = np.array(dataset['y'])

    x = np.linspace(min(x),max(x),len(x)+1)
    y = np.linspace(min(y)-0.5,max(y)+0.5,len(y)+1) + 1
    z = np.transpose(np.array(dataset['z_ch0_arr']))

    # make plot
    plt.grid(linestyle='--')
    plt.pcolormesh(x,y,z)
    plt.xlabel(dataset['x_label'])
    plt.ylabel(dataset['y_label'])
    cbar = plt.colorbar()
    cbar.set_label('counts/s')
    plt.title(dataset_name)

    # save figure
    if save_figure:
        plt.savefig(filename_png)

    # pop up
    if show_figure:
        plt.show()

def autoplot_scan2d(filename, save_figure=True):

    # load sweep
    f = open(filename)
    dataset = json.load(f)
    f.close()

    # name of dataset, to be used as plot title
    dataset_name = os.path.basename(filename).partition('.')[0]

    # path and name to save image
    filename_png = filename.replace('.json','.png')

    # process sweep
    x = np.array(dataset['x'])
    y = np.array(dataset['y'])
    z_ch0_arr = np.array(dataset['z_ch0_arr'])
    z_ch1_arr = np.array(dataset['z_ch1_arr'])

    x = np.linspace(min(x),max(x),len(x)+1)
    y = np.linspace(min(y)-0.5,max(y)+0.5,len(y)+1) + 1
    z = np.transpose(z_ch0_arr)

    # make plot
    plt.pcolormesh(x,y,z)
    plt.xlabel(dataset['x_label'])
    plt.ylabel(dataset['y_label'])
    cbar = plt.colorbar()
    cbar.set_label('counts/s')
    plt.title(dataset_name)

    if save_figure:
        plt.savefig(filename_png)

def autoplot_scan2d_unequalX(filename, save_figure=True, show_figure=False, x_shift=0):
    # best used with the "resonator_triangular" option on the M2 being manually started, i.e. the laser is continuously sweeping

    print('plotting scans...')

    # load sweep
    dataset, dataset_name = load_dataset(filename)

    # combine scans into one long list
    c = 3e8
    wav_start = np.transpose(np.array(dataset['wavelength_bin_start_ch2_arr'])).flatten()
    wav_stop = np.transpose(np.array(dataset['wavelength_bin_stop_ch2_arr'])).flatten()
    wav = (wav_start + wav_stop)/2
    f = c/wav
    f0 = (max(f)+min(f))/2
    wav0 = c/f0
    delta = f - f0

    t = np.transpose(np.array(dataset['t_bin_arr'])).flatten()
    z = np.transpose(np.array(dataset['z_ch0_arr'])).flatten()

    # create list of individual scans
    smooth_pts = 5
    f_diff_sign = np.sign(np.diff(smooth(f,smooth_pts)))
    scan_idx = np.where(f_diff_sign[:-1] != f_diff_sign[1:])[0]

    t_scans = []
    wav_scans = []
    delta_scans = []
    counts_scans = []

    last_val = 0
    for idx, val in enumerate(scan_idx):
        # get single scan
        delta_single_scan = []
        counts_single_scan = []

        t_single_scan = list(t[last_val:val])
        wav_single_scan = list(wav[last_val:val])
        delta_single_scan = list(delta[last_val:val])
        counts_single_scan = list(z[last_val:val])

        t_scans.append(t_single_scan)
        wav_scans.append(wav_single_scan)
        delta_scans.append(delta_single_scan)
        counts_scans.append(counts_single_scan)

        last_val = val

    # get minimum and maximumvalue of all scans
    for idx in range(len(counts_scans)):
        c_this_scan = counts_scans[idx]

        if idx == 0:
            c_min_all_scans = min(c_this_scan)
            c_max_all_scans = max(c_this_scan)
        else:
            if min(c_this_scan) < c_min_all_scans:
                c_min_all_scans = min(c_this_scan)
            if max(c_this_scan) > c_max_all_scans:
                c_max_all_scans = max(c_this_scan)

    # 2d color plot
    fig, ax = plt.subplots(1)
    for idx in range(len(counts_scans)):
        if idx < len(counts_scans):
            x = np.array(delta_scans[idx]) + x_shift
            y = np.array(np.ones(len(x))) * min(t_scans[idx]) / 60
            z = np.array(counts_scans[idx])

            if idx % 2 == 1:
                x = np.flip(x)
                z = np.flip(z)

            plot_colourline(x, y, z, c_min_all_scans, c_max_all_scans, linewidth=250/len(counts_scans))

    # plt.xlim([-1,1])
    # plt.xlim([-0.5,0.5])
    plt.ylim([t_scans[1][0]/60,t_scans[-1][0]/60])
    plt.xlabel('detuning (GHz) from ' + str(round(wav0,5)) + ' nm')
    plt.ylabel('time (min)')
    plt.grid()
    plt.title(dataset_name)
    fig.colorbar(mappable=None)

    print('plotting finished')

    if save_figure:
        plt.savefig(filename.replace('.json','.png'))

    if show_figure:
        plt.show()

def autoplot_vna1d(filename, plot_type='dB', save_figure=True, show_figure=False, delay_ns=0):
    # plot_type options are:
    #   "dB" for amplitude of S-parameter in dB
    #   "abs" for amplitude of S-parameter in linear units
    #   "deg" for angle of S-parameter in degrees
    #   "rad" for angle of S-parameter in radians

    print('plotting vna sweep... ' + plot_type)
    dataset, dataset_name = load_dataset(filename)

    f = np.array(dataset['f']) # GHz

    try:
        S11 = np.array(dataset['S11_Re']) + 1j*np.array(dataset['S11_Im'])
        S11 = S11 * np.exp(1j*2*np.pi*f*delay_ns)
        if plot_type=='dB':
            plt.plot(f,20*np.log10(abs(S11)),label='S11')
        elif plot_type=='abs':
            plt.plot(f,abs(S11),label='S11')
        elif plot_type=='deg':
            plt.plot(f,np.angle(S11)*180/np.pi,label='S11')
        elif plot_type=='rad':
            plt.plot(f,np.angle(S11),label='S11')
    except:
        pass

    try:
        S21 =np.array(dataset['S21_Re']) + 1j*np.array(dataset['S21_Im'])
        S21 = S21 * np.exp(1j*2*np.pi*f*delay_ns)
        if plot_type=='dB':
            plt.plot(f,20*np.log10(abs(S21)),label='S21')
        elif plot_type=='abs':
            plt.plot(f,abs(S21),label='S21')
        elif plot_type=='deg':
            plt.plot(f,np.angle(S21)*180/np.pi,label='S21')
        elif plot_type=='rad':
            plt.plot(f,np.angle(S21),label='S21')
    except:
        pass

    try:
        S12 =np.array(dataset['S12_Re']) + 1j*np.array(dataset['S12_Im'])
        S12 = S12 * np.exp(1j*2*np.pi*f*delay_ns)
        if plot_type=='dB':
            plt.plot(f,20*np.log10(abs(S12)),label='S12')
        elif plot_type=='abs':
            plt.plot(f,abs(S12),label='S12')
        elif plot_type=='deg':
            plt.plot(f,np.angle(S12)*180/np.pi,label='S12')
        elif plot_type=='rad':
            plt.plot(f,np.angle(S12),label='S12')
    except:
        pass

    try:
        S22 =np.array(dataset['S22_Re']) + 1j*np.array(dataset['S22_Im'])
        S22 = S22 * np.exp(1j*2*np.pi*f*delay_ns)
        if plot_type=='dB':
            plt.plot(f,20*np.log10(abs(S22)),label='S22')
        elif plot_type=='abs':
            plt.plot(f,abs(S22),label='S22')
        elif plot_type=='deg':
            plt.plot(f,np.angle(S22)*180/np.pi,label='S22')
        elif plot_type=='rad':
            plt.plot(f,np.angle(S22),label='S22')
    except:
        pass

    # plot
    plt.xlabel('frequency (GHz)')
    plt.legend()
    plt.title(dataset_name, size=8)
    plt.grid()

    if plot_type=='dB':
        plt.ylabel('amplitude (dB)')
    elif plot_type=='abs':
        plt.ylabel('amplitude')
    elif plot_type=='deg':
        plt.ylabel('angle (degrees)')
    elif plot_type=='rad':
        plt.ylabel('angle (rad.)')
    else:
        print('warning: plot_type must be "dB", "abs", "deg", or "rad"')

    # save
    if save_figure:
        plt.savefig(filename.replace('.json','.png'))

    # pop up
    if show_figure:
        plt.show()
