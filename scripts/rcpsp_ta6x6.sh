python3  -m psp.train_psp    --batch_size 256 \
        --conflicts clique \
        --device cuda:1 \
        --exp_name_appendix rcpsp_taillard-H64_L8 \
    --fixed_validation \
    --gae_lambda 1.0 \
    --graph_pooling learn \
    --residual_gnn \
    --hidden_dim_features_extractor 64 \
    --n_epochs 3 \
    --n_layers_features_extractor 8 \
    --n_steps_episode 9500 \
    --n_workers 10 \
    --path /data1/infantes/saved_networks/ \
    --test_dir ./instances/psp/taillards/6x6/ \
    --total_timesteps 100000000 \
    --n_j 6 \
    --n_m 6 \
    --random_taillard
