from fastai.learner import load_learner
import numpy as np
import io
from base64 import b64encode, b64decode
from itertools import compress




class Inferencer:

    def __init__(self, learner, input_type=None, output_type=None):
        self.learn = load_learner(learner)

        # get input type
        if input_type == None:
            if 'TextLearner' in str(type(self.learn)):
                self.input_type = 'text'
            else:
                self.input_type = 'image'
        else:
            self.input_type == input_type


        # get output type
        if output_type == None:
            loss_func = str(type(self.learn.loss_func))
            if 'CrossEntropy' in loss_func:
                self.output_type = 'class'
            elif 'BCEWithLogits' in loss_func:
                self.output_type = 'label'
            elif 'MSELoss' in loss_func:
                self.output_type = 'reg'
            else:
                print('no output_type defined!')
        else:
            self.output_type = output_type

        print(f'learner initialized! input: {self.input_type}, output: {self.output_type}')


    def get_image_items(self, images_b64):
        images = [b64decode(img) for img in images_b64]
        return images


    def get_dl(self, data_json):
        if self.input_type == 'image':
            if 'images' in data_json:
                items = self.get_image_items(data_json['images'])
            else:
                raise TypeError("Input type image but no images in request!")
            
        elif self.input_type == 'text':
            if 'texts' in data_json:
                items = data_json['texts']
            else:
                raise TypeError("Input type text but no texts in request!")
            
        return self.learn.dls.test_dl(items)


    # TODO: tta
    def get_preds(self, data_json):
        try:
            dl = self.get_dl(data_json)
            preds = self.learn.get_preds(dl=dl, with_decoded=True)
        except:
            raise

        return preds


    def get_results(self, preds):

        # get vocab for input_type
        if self.input_type == 'image':
            vocab = self.learn.dls.vocab
        elif self.input_type == 'text':
            vocab = self.learn.dls.vocab[1]

        # get decoded output for output_type
        if self.output_type == 'class':
            preds = preds[0]   
            preds_dec = [np.argmax(p) for p in preds.tolist()]
            labels = [vocab[pred] for pred in preds_dec]
            probabilities = [np.max(p) for p in preds.tolist()]

        if self.output_type == 'label':
            labels = []
            probabilities = []
            preds_dec = None
            for i,p in enumerate(preds[2]):
                labels.append(list(compress(vocab, p)))
                proba_float = list(map(float, preds[0][i]))
                probabilities.append(list(compress(proba_float, p)))
                
        return preds_dec, labels, probabilities







