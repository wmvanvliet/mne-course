from mne._fiff.meas_info import Info
from mne._fiff.pick import pick_info, pick_types
from mne.bem import fit_sphere_to_headshape
from mne.channels.interpolation import _do_interp_dots
from mne.epochs import BaseEpochs
from mne.evoked import Evoked
from mne.forward import _map_meg_or_eeg_channels
from mne.io import BaseRaw
from mne.utils.check import _validate_type


def move_head(inst, dest, dig_kinds="auto"):
    """Virtually move head position to a new destination.

    After this operation, the data will have the sensor layout and head position of the
    destination data.

    Parameters
    ----------
    inst : Raw | Epochs | Evoked
        The data to virtually moved. Will be modified in-place.
    dest : Raw | Epochs | Evoked | Info
        Some data with the desired head position.
    dig_kinds : list of str | str
        Kind of digitization points to use in the fitting. These can be any
        combination of ('cardinal', 'hpi', 'eeg', 'extra'). Can also
        be 'auto' (default), which will use only the 'extra' points if
        enough (more than 4) are available, and if not, uses 'extra' and
        'eeg' points.

    Notes
    -----
    As a side effect, all bad channels will be interpolated.
    """  # noqa E501
    _validate_type(dest, (BaseRaw, BaseEpochs, Evoked, Info), "dest")
    if isinstance(dest, Info):
        info_to = dest
    else:
        info_to = dest.info
    if "dev_head_t" not in info_to:
        raise ValueError(
            "Could find an MEG->head transformation in the supplied `dest`."
        )
    picks_to = pick_types(info_to, meg=True, exclude=[])
    info_to = pick_info(info_to, picks_to)

    _validate_type(inst, (BaseRaw, BaseEpochs, Evoked), "inst")
    info_from = inst.info
    if "dev_head_t" not in info_from:
        raise ValueError(
            "Could find an MEG->head transformation in the supplied `inst`."
        )
    picks_from = pick_types(info_from, exclude="bads", meg=True)
    info_from = pick_info(info_from, picks_from)

    _, origin_head, _ = fit_sphere_to_headshape(info_from, dig_kinds=dig_kinds)

    mapping = _map_meg_or_eeg_channels(
        info_from, info_to, mode="accurate", origin=origin_head
    )
    _do_interp_dots(inst, mapping, picks_from, picks_to)
    inst.info["dev_head_t"] = info_to["dev_head_t"]
