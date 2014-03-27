package com.hardwarebreakout.bleboosterdemo;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

public class LedButtonFragment extends BleFragment implements OnClickListener {
    private final static String TAG = LedButtonFragment.class.getSimpleName();

	@Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
        Bundle savedInstanceState) {
		super.onCreateView(inflater, container, savedInstanceState);
		
        // Inflate the layout for this fragment
		View v = inflater.inflate(R.layout.fragment_led_button_demo, container, false);

        Button clearButton = (Button) v.findViewById(R.id.clear_button_id);
        clearButton.setOnClickListener(this);
        Button toggleButton = (Button) v.findViewById(R.id.toggle_button_id);
        toggleButton.setOnClickListener(this);
        
        EditText buttonCount = (EditText) v.findViewById(R.id.button_count);
        buttonCount.setText("0");
        
        return v;
    }
	
	@Override
    public void onClick(View v) {
        Log.d(TAG, "onClick()" + v.getId());
        switch (v.getId()) {
	        case R.id.clear_button_id:
	        	clearButton(v);
	            break;
	        case R.id.toggle_button_id:
	        	toggleButton(v);
	        	break;
        }
    }
	
	public void toggleButton(View view) {
		sendData(new byte[] {'1'});
	}
	
	public void clearButton(View view) {
		EditText buttonCount = (EditText) getView().findViewById(R.id.button_count);
		buttonCount.setText("0");
	}
		
	public int incrementCount() {
		EditText buttonCount = (EditText) getView().findViewById(R.id.button_count);
		int newCount = Integer.parseInt(buttonCount.getText().toString()) + 1;
		buttonCount.setText(Integer.toString(newCount));
		return newCount;
	}  
        
    public void dataReceived(byte[] data) {    	
    	for (int i = 0; i < data.length; i++) {
			Log.d(TAG, String.format("Raw data: %d", data[i]));
    		if (data[i] == 'b') {
    			int buttonCount = incrementCount();
    			Log.d(TAG, String.format("Button pressed: %d", buttonCount));
    		}
    	}
    }
}
