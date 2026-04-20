unsigned int iter = 0;
bool is_signing = false;
unsigned int num_signing = 5;
unsigned wait_ms = 2000

if (A1 && !is_signing) is_signing = true;
else if (A1 && is_signing) iter = 0;
else if (!A1 && is_signing) iter++;

if (i > 2000 && num_signing != 0) {
    num_signing--;
    iter = 0;
    upload_data(signature);
    clear_whiteboard();
}

unsigned int iter = 0;
bool is_signing = false;
unsigned wait_ms = 2000
verify_sig = false;

if (A1 && !is_signing) is_signing = true;
else if (A1 && is_signing) iter = 0;
else if (!A1 && is_signing) iter++;

if (i > 2000 && num_signing != 0) {
    iter = 0;
    upload_data(signature);
    verify_sig = verify_svm_classfier();
    clear_whiteboard();
}



