package com.hardwarebreakout.bleboosterdemo;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class TerminalFragment extends BleFragment implements OnClickListener{
	
	@Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
        Bundle savedInstanceState) {
		
        // Inflate the layout for this fragment
		View v = inflater.inflate(R.layout.fragment_terminal_demo, container, false);
        
        Button stringSendButton = (Button) v.findViewById(R.id.string_send_button_id);
        stringSendButton.setOnClickListener(this);
        Button hexSendButton = (Button) v.findViewById(R.id.hex_send_button_id);
        hexSendButton.setOnClickListener(this);

        return v;
    }

	@Override
	public void dataReceived(byte[] data) {				
		TextView receiveText = (TextView) getView().findViewById(R.id.receive_text_id);		
		receiveText.append(new String(data));
	}
	
	@Override
    public void onClick(View v) {
        switch (v.getId()) {
	        case R.id.string_send_button_id:
	    		EditText stringInput = (EditText) getView().findViewById(R.id.string_send_text_id);
	        	sendString(stringInput.getText().toString());
	        	stringInput.setText("");
	            break;
	        case R.id.hex_send_button_id:
	    		EditText hexInput = (EditText) getView().findViewById(R.id.hex_send_text_id);
	    		sendHex(hexInput.getText().toString());
	    		hexInput.setText("");
	        	break;
        }
    }
	
	public void sendString(String string) {
		byte[] data = string.getBytes();
		sendData(data);
	}
	
	public void sendHex(String string) {
		String[] numbers = string.split("[ ]");
		byte[] data = new byte[numbers.length];
		for (int i = 0; i < numbers.length; i++)
			data[i] = (byte)(short)Short.decode(numbers[i]);
		sendData(data);
	}
}
