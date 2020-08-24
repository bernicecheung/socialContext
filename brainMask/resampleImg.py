dimport argparse
import nilearn

if __name__ == "__main__":
    # define import arguments
    parser = argparse.ArgumentParser(description='Resample features')
    parser.add_argument('--target', dest='target', default='', help='Path to the target image')
    parser.add_argument('--rsinput', dest='rsinput', default='', help='Input directory')
    parser.add_argument('--output', dest='output', default='', help='Output')
    
    # generate inputs
    inputs = parser.parse_args()
    
    resamp_img = nilearn.image.resample_to_img(inputs.rsinput,inputs.target)
    
    resamp_img.to_filename(inputs.output)
