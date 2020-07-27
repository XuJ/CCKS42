gcloud config set project spherical-treat-280701
gcloud config set compute/zone europe-west4-a

gcloud compute instances create jxvm \
       --machine-type=n1-highmem-4 \
       --image-project=ubuntu-os-cloud \
       --image-family=ubuntu-1804-lts  \
       --boot-disk-size=250g \
       --scopes=cloud-platform \
	   --preemptible
ctpu up --tpu-size=v3-8 --zone=europe-west4-a --tf-version=1.15 --name jxtpu --tpu-only
ctpu up --tpu-size=v3-8 --zone=europe-west4-a --tf-version=1.15 --name jxtpu2 --tpu-only
ctpu rm --zone=europe-west4-a --name jxtpu3 --tpu-only
ctpu rm --zone=europe-west4-a --name jxtpu4 --tpu-only
 
gcloud compute instances list --zones=europe-west4-a
gcloud compute tpus list --zone=europe-west4-a

########################################################################################

gcloud config set project spherical-treat-280701
gcloud compute ssh --zone europe-west4-a jxvm

########################################################################################

sudo apt-get update
sudo apt-get install python3-pip
python3 -m pip install --upgrade pip
pip3 install stanza scipy sklearn tensorflow==1.15.2
pip3 install --upgrade google-api-python-client oauth2client

git clone https://github.com/XuJ/Chinese-ELECTRA.git -b dev

gsutil ls -r gs://ccks/electra/
gsutil ls -r gs://ccks/electra/finetuning_data/
python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ner"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu", "do_eval": true, "do_test": false, "write_test_outputs": false, "use_tfrecords_if_existing": false, "do_train": true, "max_seq_length": 512, "max_answer_length": 64}' && python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ner"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu", "do_eval": false, "do_test": true, "write_test_outputs": true, "use_tfrecords_if_existing": false, "do_train": false, "max_seq_length": 512, "max_answer_length": 64}'

python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ccks42ec", "ccks42num"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu2", "do_eval": true, "do_test": false, "write_test_outputs": false, "use_tfrecords_if_existing": false, "do_train": true, "max_seq_length": 512}' && python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ccks42ec", "ccks42num"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu2", "do_eval": false, "do_test": true, "write_test_outputs": true, "use_tfrecords_if_existing": false, "do_train": false, "max_seq_length": 512}'

python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ccks42ee"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu2", "do_eval": true, "do_test": false, "write_test_outputs": false, "use_tfrecords_if_existing": false, "do_train": true, "max_seq_length": 512, "max_answer_length": 64}' && python3 run_finetuning.py \
    --data-dir  gs://ccks/electra/ \
    --model-name electra_large \
    --hparams '{"model_size": "large", "task_names": ["ccks42ee"], "use_tpu": true, "num_tpu_cores": 8, "vocab_size": 21128, "tpu_name": "jxtpu2", "do_eval": false, "do_test": true, "write_test_outputs": true, "use_tfrecords_if_existing": false, "do_train": false, "max_seq_length": 512, "max_answer_length": 64}'

	
gsutil mv gs://ccks2020/electra/finetuning_data/ccks42ee/eval.json gs://ccks2020/electra/finetuning_data/ccks42ee/backup.json
gsutil cp gs://ccks2020/electra/finetuning_data/ccks42ee/train.json gs://ccks2020/electra/finetuning_data/ccks42ee/eval.json
gsutil cp gs://ccks/electra/finetuning_data/ccks42ee/train.json gs://ccks/electra/finetuning_data/ner/train.json
gsutil cp gs://ccks/electra/finetuning_data/ccks42ee/dev.json gs://ccks/electra/finetuning_data/ner/dev.json
gsutil cp gs://ccks/electra/finetuning_data/ccks42ee/eval.json gs://ccks/electra/finetuning_data/ner/eval.json

	
	
	
	
gsutil acl ch -u service-1094367779166@cloud-tpu.iam.gserviceaccount.com:WRITER gs://squad_cx

python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=electra_large   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "z1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 10, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' | tee log


python3 build_pretraining_dataset.py --corpus-dir=./data --vocab-file=gs://squad_cx/electra_data/models/chinese_electra_base/vocab.txt --output-dir=gs://squad_cx/electra_data/pretrain_tfrecords --max-seq-length=512

python3 run_pretraining.py --data-dir=gs://squad_cx/electra_data --model-name=chinese_electra_base2 --hparams '{"model_size": "base", "num_train_steps": 10000, "num_warmup_steps": 100, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "sugarholdh", "train_batch_size": 256, "max_seq_length": 512, "learning_rate": 2e-4, "vocab_size": 21128, "do_train": false, "do_eval": true}'

git clone https://github.com/HuaYZhao/electra.git -b atrl




tmux attach -t 0



gsutil cp -r gs://squad_cx/electra_data/models/electra_large/finetuning_models_bk/squad_model_2 gs://squad_cx/electra_data/models/atrl8862
gsutil cp gs://squad_cx/electra_data/models/electra_large/vocab.txt gs://squad_cx/electra_data/models/atrl8862/vocab.txt

sudo apt-get update
sudo apt-get install python3-pip
python3 -m pip install --upgrade pip
pip3 install stanza scipy sklearn tensorflow==1.15.2
pip3 install --upgrade google-api-python-client oauth2client

gsutil cp gs://squad_cx/electra_data/finetuning_data/squad/train.json gs://squad_cx/electra_data/finetuning_data/squad/dev.json

gsutil -m cp -r gs://squad_cx/electra_data/models/electra_large/finetuning_models_8876reg/* gs://squad_cx/electra_data/models/

gsutil cp data/dev.json gs://squad_cx/electra_data/finetuning_data/squad/dev.json

gsutil cp -r gs://squad_cx/electra_data/models/electra_large/vocab.txt gs://squad_cx/electra_data/models/squad_model_1/

gsutil -m cp -r gs://squad_cx/electra_data/models/electra_large/finetuning_tfrecords gs://squad_cx/electra_data/models/squad_model_1/

gsutil cp -r gs://squad_cx/electra_data/models/squad_model_2 gs://squad_cx/electra_data/models/reg_model

gsutil -m cp -r gs://squad_cx/electra_data gs://squad_cx/electra_data_atpv

gsutil -m cp -r gs://squad_cx/electra_data/models/electra_large/finetuning_models gs://squad_cx/electra_data/models/electra_large/finetuning_models_8876reg


python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_1   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_2   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_3   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_4   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_5   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_6   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_7   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_8   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_9   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' && python3 run_finetuning.py   --data-dir=gs://squad_cx/electra_data --model-name=squad_model_10   --hparams '{"model_size": "large", "task_names": ["squad"], "num_train_epochs": 2, "use_tpu": true, "num_tpu_cores": 8, "tpu_name": "c1", "train_batch_size": 32, "eval_batch_size": 32, "predict_batch_size": 32, "max_seq_length": 128, "learning_rate": 5e-05, "use_tfrecords_if_existing": true, "num_trials": 1, "do_train": false, "do_eval": true, "save_checkpoints_steps": 100000 }' 


gsutil -m cp -r gs://squad_cx/electra_data/models/electra_large/finetuning_models_8876reg/squad_model_4 gs://squad_cx/electra_data/models/8876reg_model
