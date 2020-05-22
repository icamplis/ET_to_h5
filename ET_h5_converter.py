# imports
import os
from parser import get_args
from helpers import data_loader, check_and_get_ET_files, make_dfs, create_combined_df


def convert(path, combined, bids):

    first_entry = True  # to open an HDF file.
    exp_folder, hdf_output_file, subj_folders = data_loader(path, bids)

    # Walk through subject-wise data folders.
    for sub_subject in subj_folders:

        subj, subj_full_path, ET_files = check_and_get_ET_files(sub_subject, exp_folder)

        # iterate through files
        for f in ET_files:

            # check if all files start with 'sub-' + subject ID
            begin = 'sub-' + subj
            if not (f[:len(begin)] == begin or f.split('_')[0] == begin):
                print('Mismatch between subj-ID and filename at subj file:\n --> %s' % os.path.join(subj_full_path, f))

            sess_name, ext = os.path.splitext(f)

            # iterate over tasks
            if ext == '.asc':

                task_name, times_df, saccs_df, fixes_df, blinks_df = make_dfs(sess_name, f, subj_full_path)

                session_ID = subj + '/' + task_name

                # write to hdf
                if first_entry:
                    times_df.to_hdf(hdf_output_file, session_ID, mode='w')
                    first_entry = False
                else:
                    times_df.to_hdf(hdf_output_file, session_ID, mode='a')

                saccs_df.to_hdf(hdf_output_file, session_ID + '_saccades', mode='a')
                fixes_df.to_hdf(hdf_output_file, session_ID + '_fixations', mode='a')
                blinks_df.to_hdf(hdf_output_file, session_ID + '_blinks', mode='a')

                if combined:
                    combined_df = create_combined_df(times_df, saccs_df, fixes_df, blinks_df)
                    combined_df.to_hdf(hdf_output_file, session_ID + '_combined', mode='a')


if __name__ == "__main__":
    args = get_args()
    convert(args.path, args.combined, args.BIDS)
