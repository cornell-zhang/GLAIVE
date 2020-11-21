#!/usr/bin/perl
use Scalar::Util 'looks_like_number';
use List::Util qw[min max];

my $SCRIPTS_DIR = "$ENV{APPROXGEM5}/gem5/scripts/injections/";
my $USERNAME = $ENV{LOGNAME};

my $numArgs = $#ARGV + 1;
if($numArgs != 3) {
        print "Usage: perl detailed_app_level_analysis.pl <app_name> <output_file> <id>(set as random string if running script individually) \n";
        die;
}
my $app_name = $ARGV[0];
my $output_file = $ARGV[1];
my $id = $ARGV[2];
my $GOLDEN_DIR = "/scratch/$USERNAME/m5out_$id";

sub get_max	#get the max of two numbers
{
    return max($_[0],$_[1]);
	local($a, $b, $m);
	$m = -1;
	($a, $b) = ($_[0], $_[1]);
	if($a > $b)
	{
		$m = $a;
	}
	else
	{
		$m = $b;
	}
	
	if ($m == -1)
	{
		die;
	}
	return $m;
}

sub get_min	#get the min of two numbers
{
    return min($_[0], $_[1]);
	local($a, $b, $m);
	$m = 123456789;
	($a, $b) = ($_[0], $_[1]);
	if($a < $b)
	{
		$m = $a;
	}
	else
	{
		$m = $b;
	}
	
	if ($m == 123456789)
	{
		die;
	}
	return $m;

}

sub get_average #get the average from total and number of items
{
	local($tot, $num, $av);
	($tot, $num) = ($_[0], $_[1]);
	$av = ($tot/$num);
	return $av;
}


sub get_abs_diff	#get the absolute diffrence of two numbers
{
	local($a, $b, $diff);
	($a, $b) = ($_[0], $_[1]);
	$diff = abs($a - $b);
	return $diff;
	
}

sub get_error_percent   #get the error percentage compared to golden value
{
	local($g_value, $error, $p);
	($g_value, $error) = ($_[0], $_[1]);
	if($g_value == 0) #in blackscholes one of the outputs is golden file is zero. It has been recorded.
	{
		#assign it a really small value so that there is no divide by zero error.
		$g_value = 0.0000000000000000001;
		#print "Sub $error\n";
	}
	#sometimes if the g_val is negative the error percentage is negative
	#take care of this by getting the abs value at the function call site.
	$p = ($error/$g_value)*100;
	return $p;
}

if($app_name eq "blackscholes_simlarge" || $app_name eq "blackscholes_input_run_00000"
     || $app_name eq "blackscholes_run_00000"
     || $app_name eq "blackscholes_run_00001"
     || $app_name eq "blackscholes_run_00002"
     || $app_name eq "blackscholes_run_00003"
     || $app_name eq "blackscholes_run_00004"
     || $app_name eq "blackscholes_run_full"
     || $app_name eq "blackscholes_run_5"
     || $app_name eq "blackscholes_run_1k"
     || $app_name eq "blackscholes_run_21_a"
     || $app_name eq "blackscholes_run_21_b"
     || $app_name eq "blackscholes_run_32"
     || $app_name eq "blackscholes_run_64"
     || $app_name eq "blackscholes_run_128"
     || $app_name =~ /blackscholes/ 
     || $app_name eq "blackscholes_input_run_00001"
     || $app_name eq "blackscholes_input_run_00002"
     || $app_name eq "blackscholes_input_run_00003"
     || $app_name eq "blackscholes_input_run_00004") {
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} else {
		my $acceptability = 1000;
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my ($num_weird_val, $weird_val, $legit_val, $g_val_zero, $g_val_zero_num, $negetive_val) = 0;
		my ($num_diffs, $rse, $num_items, $av_faulty_value, $av_golden_value, $av_rel_err) = 0;
		#my $num_tot = 0;
		my ($tot_diff, $tot_err_percent, $tot_se, $tot_faulty_value, $tot_golden_value)=0; 
		my ($min_diff, $max_diff, $min_percent, $max_percent, $average, $max_faulty_val, $min_faulty_val); 
		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		if($#g_lines != $#f_lines) {
			$acceptability = "Eggregious-line_num_mismatch";
			#$eggregious = 1;
		} else {
			foreach $i (0 .. $#g_lines) { 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];
				chomp($g_line);
				chomp($f_line);
				
				$tot_faulty_value += $f_line;
				$tot_golden_value += $g_line;

				if($g_line ne $f_line)
				{
					$num_diffs++;

					#normal values in the outputs are numeric. Log if there is anything else that is weird.(Nan, Infinity, alphanumeric, negetive)
					# Since this is a financial application, negetive value is probably wrong.
					#(option price or stock price cannot be negetive - http://164.67.163.139/documents/areas/fac/finance/negativeoptionprices.pdf)
	
					if((not looks_like_number($f_line)) or ($f_line =~ /[a-zA-Z]/) or ($f_line != abs($f_line)))
					{
						#print "WEIRD VALUE\n";
						$num_weird_val++;
						$weird_val = 1;
						$legit_val = 0;
					}
					else
					{
						$legit_val = 1;
					}

					if($f_line != abs($f_line))
					{
						$negetive_val = 1;
					}
					#sometimes the golden value is zero. This is bad since the relative error (error percentage) is undefined as the denominator is 0
					#log these cases. Change has been made in the get_error_percent to make take care of this.

					if($g_line == 0)
					{
						$g_val_zero = 1;
						$g_val_zero_num++;
						#print "ZEro golden value\n";	
					}
					if ($legit_val == 1)
					{

						my $diff = &get_abs_diff($g_line, $f_line);
						#print "Diff $i $g_line, $f_line, $diff\n";
						my $err_percent = abs(get_error_percent($g_line, $diff));
						my $se = ($diff*$diff); #square error
						$tot_diff += $diff;
						$tot_err_percent += $err_percent;
						$tot_se += $se;
						if($num_diffs == 1)
						{
							$min_diff = $diff;
							$max_diff = $diff;
							$min_percent = $err_percent;
							$max_percent = $err_percent;
							$max_faulty_val = $f_line;
							$min_faulty_val = $f_line;		
							#$av_percent = $err_percent;
						}
						else
						{

							$min_diff = &get_min($diff, $min_diff);
							$max_diff = &get_max($diff, $max_diff);
							#$av_diff = $diff;
							$min_percent = &get_min($err_percent, $min_percent);
							$max_percent = &get_max($err_percent, $max_percent);
							$max_faulty_val = &get_max($f_line, $max_faulty_val);
							$min_faulty_val = &get_min($f_line, $min_faulty_val);
						}
					}
					
				}
			}
			$rse = sqrt($tot_se);
			$num_items = $#g_lines+1;
			$av_faulty_value = ($tot_faulty_value/$num_items);
			$av_golden_value = ($tot_golden_value/$num_items);
			my $av_diff = &get_abs_diff($av_golden_value, $av_faulty_value);
			$av_rel_err = &get_error_percent($av_golden_value, $av_diff); 
			$acceptability = "Tolerable";
		}
		printf ("SDC:%s;%d,%d,%d,%d,%.18f,%.18f,%.18f,%f,%f,%f,%.18f,%d,%d,%.18f,%.18f,%f,%f,%f,%d\n",$acceptability,$weird_val, $num_weird_val, $g_val_zero, $g_val_zero_num, $min_diff, $max_diff, $tot_diff, $min_percent, $max_percent, $tot_err_percent, $rse, $num_items, $num_diffs, $av_faulty_value, $av_golden_value, $av_rel_err, $max_faulty_val, $min_faulty_val, $negetive_val);
		# print "number of differences = $num_diffs\n";
	}
} 
elsif ($app_name eq "swaptions_simsmall" || $app_name eq "swaptions_simsmall_large"
    || $app_name =~ /swaptions/ 
    || $app_name eq "swaptions_run_input" )
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} else {
		my $acceptability = 1000;
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		#are there any weird values(apart from numeric values)?, is there a NaN value in output (0 for no, 1 for yes)
		#are there any negative value, is there any other weird alphanumeric values in the faulty output?
		my ($p_num_weird_val, $p_weird_val, $legit_val, $e_legit_val, $e_num_weird_val, $e_weird_val, $negetive_val, $num_negetive_val) = 0;
		my ($p_num_diffs, $e_num_diffs, $p_rse, $e_rse, $num_items) = 0;
		my ($p_av_faulty_value, $p_av_golden_value,$p_av_rel_err, $e_av_faulty_value, $e_av_golden_value,$e_av_rel_err ) = 0;
		my ($p_tot_diff, $p_tot_err_percent, $p_tot_se, $p_tot_faulty_value, $p_tot_golden_value)=0; #keep track of changes in price (p)
		my ($p_min_diff, $p_max_diff, $p_min_percent, $p_max_percent, $p_average)=0;
                my ($e_tot_diff, $e_tot_err_percent, $e_tot_se, $e_tot_faulty_value, $e_tot_golden_value)=0; #keep track of changes in error (e)
		my ($e_min_diff, $e_max_diff, $e_min_percent, $e_max_percent, $e_average)=0;
		my ($p_max_faulty_val, $p_min_faulty_val, $e_max_faulty_val, $e_min_faulty_val)= 0;
		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		if($#g_lines != $#f_lines) {
			$acceptability = "Eggregious-line_num_mismatch";
		} else {
			foreach $i (0 .. $#g_lines) { 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];

				if($g_line !~ /SwaptionPrice/) {
					next;
				}

				chomp($g_line);
				chomp($f_line);
			        $num_items++;	
				my @g_words = split(/:/,$g_line);
				my @f_words = split(/:/,$f_line);
#				you are looking at elements [2] and [3], [2] is price, [3] is error
				$g_words[2] =~ s/[a-zA-Z]//g;
				$g_words[2] =~ s/\s//g;
				#$f_words[2] =~ s/[a-zA-Z]//g;
				$f_words[2] =~ s/StdError//g;
				$f_words[2] =~ s/\s//g;
				$f_price = $f_words[2];
				$g_price = $g_words[2];

				$g_words[3] =~ s/\]//g;
				$f_words[3] =~ s/\]//g;
				$g_words[3] =~ s/\s//g;
				$f_words[3] =~ s/\s//g;
				$f_error = $f_words[3];
				$g_error = $g_words[3];

				
								
				#print ("5: $g_price, $f_price, $g_error, $f_error\n");			
	
				$p_tot_faulty_value += $f_price;
				$p_tot_golden_value += $g_price;
				$e_tot_faulty_value += $f_error;
				$e_tot_golden_value += $g_error;

				#calculate difference in the price
				if($g_price != $f_price)
				{
					$p_num_diffs++;
					
					#normal values in the outputs are numeric. Log if there is anything else that is weird.(Nan, Infinity, alphanumeric, negetive)
					# Since this is a financial application, negetive value is probably wrong.
					#(option price or stock price cannot be negetive - http://164.67.163.139/documents/areas/fac/finance/negativeoptionprices.pdf)
	
					if((not looks_like_number($f_price)) or ($f_price =~ /[a-zA-Z]/))
					{
						#print "WEIRD VALUE\n";
						$p_num_weird_val++;
						$p_weird_val = 1;
						$legit_val = 0;
					}
					else
					{
						$legit_val = 1;
					}

					if($f_price != abs($f_price))
					{
						$negetive_val = 1;
					}

					if ($legit_val == 1)
					{
						my $p_diff = &get_abs_diff($g_price, $f_price);
						#print "4: $p_diff,$g_price, $f_price \n";
						my $p_err_percent = abs(&get_error_percent($g_price, $p_diff));
						my $p_se = ($p_diff*$p_diff); #square error
						$p_tot_diff += $p_diff;
						$p_tot_err_percent += $p_err_percent;
						$p_tot_se += $p_se;

						if ($p_num_diffs == 1)
						{
							$p_min_diff = $p_diff;
							$p_max_diff = $p_diff;
							$p_min_percent = $p_err_percent;
							$p_max_percent = $p_err_percent;
							$p_max_faulty_val = $f_price;
							$p_min_faulty_val = $f_price;	
						}
						else
						{
							$p_min_diff = &get_min($p_diff, $p_min_diff);
							$p_max_diff = &get_max($p_diff, $p_max_diff);
							$p_min_percent = &get_min($p_err_percent, $p_min_percent);
							$p_max_percent = &get_max($p_err_percent, $p_max_percent);
							$p_max_faulty_val = &get_max($f_price, $p_max_faulty_val);
							$p_min_faulty_val = &get_min($f_price, $p_min_faulty_val);	
	
						}
					}

				}

				if($g_error != $f_error)
				{
					$e_num_diffs++;

					#even for standard error, check if it is a legitimate value
					#check if it is a number and then if it is not a NaN or Inf or any doesn't have an alphanumeric(hex or something)
					#if it is negetive also we flag it (standard error is a variation of standard deviation so can't be negative)

					if((not looks_like_number($f_error)) or ($f_error =~ /[a-zA-Z]/) or ($f_error != abs($f_error)))
					{
						#print "WEIRD VALUE\n";
						$e_num_weird_val++;
						$e_weird_val = 1;
						$e_legit_val = 0;
					}
					else
					{
						$e_legit_val = 1
					}

					if ($e_legit_val == 1)
					{	
						my $e_diff = &get_abs_diff($g_error, $f_error);
						#print "3E: $e_diff,$g_error, $f_error \n";

						my $e_err_percent = abs(get_error_percent($g_error, $e_diff));
						my $e_se = ($e_diff*$e_diff); #square error
						$e_tot_diff += $e_diff;
						$e_tot_err_percent += $e_err_percent;
						$e_tot_se += $e_se;
					
						if ($e_num_diffs == 1)
						{
							$e_min_diff = $e_diff;
							#print "1: $e_min_diff\n";
							$e_max_diff = $e_diff;
							$e_min_percent = $e_err_percent;
							$e_max_percent = $e_err_percent;	
						}
						else
						{
							$e_min_diff = &get_min($e_diff, $e_min_diff);
							#print "2: $e_min_diff\n";
							$e_max_diff = &get_max($e_diff, $e_max_diff);
							$e_min_percent = &get_min($e_err_percent, $e_min_percent);
							$e_max_percent = &get_max($e_err_percent, $e_max_percent);
	
						}
					}
				}

			} #end of foreach
			
			$p_rse = sqrt($p_tot_se);
			$p_av_faulty_value = ($p_tot_faulty_value/$num_items);
			$p_av_golden_value = ($p_tot_golden_value/$num_items);
			my $p_av_diff = &get_abs_diff($p_av_golden_value, $p_av_faulty_value);
			$p_av_rel_err = &get_error_percent($p_av_golden_value, $p_av_diff); 

			$e_rse = sqrt($e_tot_se);
			$e_av_faulty_value = ($e_tot_faulty_value/$num_items);
			$e_av_golden_value = ($e_tot_golden_value/$num_items);
			my $e_av_diff = &get_abs_diff($e_av_golden_value, $e_av_faulty_value);
			$e_av_rel_err = &get_error_percent($e_av_golden_value, $e_av_diff); 
			$acceptability = "Tolerable";	
		}
		#print "SDC $acceptability\n";
		# print "number of differences = $num_diffs\n";
		printf ("SDC:%s;%d,%d,%.10f,%.10f,%.10f,%f,%f,%f,%.10f,%d,%d,%.10f,%.10f,%f@%d,%d,%.10f,%.10f,%.10f,%f,%f,%f,%.10f,%d,%d,%.10f,%.10f,%f@%f,%f,%d\n",$acceptability, $p_weird_val, $p_num_weird_val, $p_min_diff, $p_max_diff, $p_tot_diff, $p_min_percent, $p_max_percent, $p_tot_err_percent, $p_rse, $num_items, $p_num_diffs, $p_av_faulty_value, $p_av_golden_value, $p_av_rel_err, $e_weird_val, $e_num_weird_val,$e_min_diff, $e_max_diff, $e_tot_diff, $e_min_percent, $e_max_percent, $e_tot_err_percent, $e_rse, $num_items, $e_num_diffs, $e_av_faulty_value, $e_av_golden_value, $e_av_rel_err, $p_max_faulty_val, $p_min_faulty_val, $negetive_val );

	}

} 
elsif ($app_name eq "water_small" || $app_name =~ /water_run/ || $app_name eq "water_run_min0" || $app_name eq "water_run_min")
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "")
	{
		print "Masked\n";
	} 
	else
	{
		my $acceptability = 1000;
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		my @A, @A_time;
		my @B, @B_time;
		my ($A_index, $B_index, $A_time_index, $B_time_index, ) = 0;
		my $start = 0;
		my $timing_start = 0;

		my ($num_weird_val, $weird_val, $legit_val) = 0;
		my ($num_diffs, $rse, $num_items, $av_faulty_value, $av_golden_value, $av_rel_err) = 0;
		#my $num_tot = 0;
		my ($tot_diff, $tot_err_percent, $tot_se, $tot_faulty_value, $tot_golden_value)=0; 
		my ($min_diff, $max_diff, $min_percent, $max_percent, $average);
		my ($max_faulty_val, $min_faulty_val)= 0;

		my ($t_num_weird_val, $t_weird_val) = 0;
		my ($t_num_diffs, $t_rse, $t_num_items, $t_av_faulty_value, $t_av_golden_value, $t_av_rel_err) = 0;
		#my $num_tot = 0;
		my ($t_tot_diff, $t_tot_err_percent, $t_tot_se, $t_tot_faulty_value, $t_tot_golden_value)=0; 
		my ($t_min_diff, $t_max_diff, $t_min_percent, $t_max_percent, $t_average);

		my $timing_val_mismatch = 0; #1 means that the number of values for the timing info is not
		#the same between the golden and faulty values. Equivalent to eggregious mismatch (for timing vals)

		foreach $i (0 .. $#g_lines)
		{ 
			my $g_line = $g_lines[$i];

			if($g_line =~ /NEW RUN/) {
				$start = 1;
				($A_index) = 0;
				next;
			}
			if($g_line =~ /COMPUTESTART/) {
				$start = 0;
				$timing_start = 1;
				#next;
			}
			if($g_line =~ /Exited Happily/) {
				$timing_start = 0;
				next;
			}


			if($start == 1)
			{
				chomp($g_line);
				my @g_words = split(/\s+/,$g_line);
				foreach $g_word (@g_words)
				{ 
					if($g_word ne "")
					{
						# print "$g_word-";
						$A[$A_index] = $g_word;
						$A_index += 1;
					}
				}

			}

			if($timing_start == 1)
			{
				# print $g_line;
				# print $f_line;
				chomp($g_line);
				my @g_words = split(/=/,$g_line);
				my $g_time_val = $g_words[1];
				$g_time_val=~ s/\s//g;
				if($g_time_val ne "")
				{	
					$A_time[$A_time_index] = $g_time_val;
					$A_time_index += 1;
				}
			}

		}#end of foreach

		#create the arrays for faulty data
		$start = 0;
		$timing_start = 0;
		foreach $i (0 .. $#f_lines)
		{ 
			my $f_line = $f_lines[$i];

			if($f_line =~ /NEW RUN/) {
				$start = 1;
				$B_index = 0;
				next;
			}
			if($f_line =~ /COMPUTESTART/) {
				$start = 0;
				$timing_start = 1;
				#next;
			}
			if($f_line =~ /Exited Happily/) {
				$timing_start = 0;
				next;
			}


			if($start == 1)
			{
				chomp($f_line);
				my @f_words = split(/\s+/,$f_line);
			
				foreach $f_word (@f_words) 
				{ 
					if($f_word ne "")
					{
						# print "$f_word-";
						$B[$B_index] = $f_word;
						$B_index += 1;
					}
				}
			}

			if($timing_start == 1)
			{
				# print $g_line;
				# print $f_line;
				chomp($f_line);
				my @f_words = split(/=/,$f_line);
				my $f_time_val = $f_words[1];
				$f_time_val=~ s/\s//g;
				if($f_time_val ne "")
				{	
					$B_time[$B_time_index] = $f_time_val;
					$B_time_index += 1;
				}	
			}

		}#end of foreach

		#created the A_time & B_time array
		

		#print "A, B, are created : $A_index, $B_index\n";
		if($#A != $#B)
		{
			$acceptability = "Eggregious-line_num_mismatch";
		}
		else
		{
			for ($i=0; $i<$A_index; $i++)
			{
		 		#print "1 $A[$i] $B[$i]\n";
		 		my $g_val = $A[$i];
				my $f_val = $B[$i];
				$tot_faulty_value += $f_val;
				$tot_golden_value += $g_val;

				if($g_val != $f_val) 
				{
					$num_diffs++;
					#log if this is a weird number/alphanumeric.
					#Negetive is ok. Potentials/forces can be negetive
					if(not looks_like_number($f_val) or ($f_val =~ /[a-zA-Z]/))
					{
						#print "WEIRD VALUE\n";
						$num_weird_val++;
						$weird_val = 1;
						$legit_val = 0;
					}
					else
					{
						$legit_val = 1
					}

					if ($legit_val == 1)
					{
						my $diff = &get_abs_diff($g_val, $f_val);
						#print "Diff $i $g_line, $f_line, $diff\n";
						#some of the g_val here is negetive. So get absolute value of error
						my $err_percent = abs(&get_error_percent($g_val, $diff));
						my $se = ($diff*$diff); #square error
						$tot_diff += $diff;
						$tot_err_percent += $err_percent;
						$tot_se += $se;
						if($num_diffs == 1)
						{
							$min_diff = $diff;
							$max_diff = $diff;
							$min_percent = $err_percent;
							$max_percent = $err_percent;
							#$av_percent = $err_percent;
							$max_faulty_val = $f_val;
							$min_faulty_val = $f_val;
						}
						else
						{
							$min_diff = &get_min($diff, $min_diff);
							$max_diff = &get_max($diff, $max_diff);
							#$av_diff = $diff;
							$min_percent = &get_min($err_percent, $min_percent);
							$max_percent = &get_max($err_percent, $max_percent);
							$max_faulty_val = &get_max($f_val, $max_faulty_val);
							$min_faulty_val = &get_min($f_val, $min_faulty_val);

						}
					}
					
				} #end for if A[$i] != $B[$i]
			} #end of cycling through the A&B arrays

			$rse = sqrt($tot_se);
			$num_items = $#A+1;
			$av_faulty_value = ($tot_faulty_value/$num_items);
			$av_golden_value = ($tot_golden_value/$num_items);
			my $av_diff = &get_abs_diff($av_golden_value, $av_faulty_value);
			$av_rel_err = &get_error_percent($av_golden_value, $av_diff); 
			$acceptability = "Tolerable";
		} 
		
		#start comparison for the timing numbers
		if($#A_time != $#B_time)
		{
			$timing_val_mismatch = 1;
		}
		else
		{
			for ($i=0; $i<$A_time_index; $i++)
			{
		 		#print "2 $A_time[$i] $B_time[$i]\n";
		 		my $g_val = $A_time[$i];
				my $f_val = $B_time[$i];
				$t_tot_faulty_value += $f_val;
				$t_tot_golden_value += $g_val;

				if($g_val != $f_val) 
				{
					$t_num_diffs++;
					#log if this is a weird number/alphanumeric/negetive.
					if(not looks_like_number($f_val) or ($f_val =~ /[a-zA-Z]/))
					{
						#print "WEIRD VALUE\n";
						$t_num_weird_val++;
						$t_weird_val = 1;
						$legit_val = 0;
					}
					else
					{
						$legit_val = 1
					}

					if ($legit_val == 1)
					{
						my $diff = &get_abs_diff($g_val, $f_val);
						#print "Diff $i $g_line, $f_line, $diff\n";
						#some of the g_val here is negetive. So get absolute value of error
						my $err_percent = abs(&get_error_percent($g_val, $diff));
						my $se = ($diff*$diff); #square error
						$t_tot_diff += $diff;
						$t_tot_err_percent += $err_percent;
						$t_tot_se += $se;
						if($t_num_diffs == 1)
						{
							$t_min_diff = $diff;
							$t_max_diff = $diff;
							$t_min_percent = $err_percent;
							$t_max_percent = $err_percent;
							#$av_percent = $err_percent;
						}
						else
						{
							$t_min_diff = &get_min($diff, $t_min_diff);
							$t_max_diff = &get_max($diff, $t_max_diff);
							#$av_diff = $diff;
							$t_min_percent = &get_min($err_percent, $t_min_percent);
							$t_max_percent = &get_max($err_percent, $t_max_percent);
						}
					}
					
				} #end for if A_time[$i](g_val) != $B_time[$i](f_val)
			} #end of cycling through the A&B arrays

			$t_rse = sqrt($t_tot_se);
			$t_num_items = $#A_time+1;
			$t_av_faulty_value = ($t_tot_faulty_value/$t_num_items);
			$t_av_golden_value = ($t_tot_golden_value/$t_num_items);
			my $t_av_diff = &get_abs_diff($t_av_golden_value, $t_av_faulty_value);
			$t_av_rel_err = &get_error_percent($t_av_golden_value, $t_av_diff); 
		}

		#print "SDC $acceptability\n";
		# print "number of differences = $num_diffs\n";
		printf ("SDC:%s;%d,%d,%.6f,%.6f,%.6f,%f,%f,%f,%.6f,%d,%d,%.6f,%.6f,%f@%d,%d,%d,%.6f,%.6f,%.6f,%f,%f,%f,%.6f,%d,%d,%.6f,%.6f,%f@%f,%f\n",$acceptability,$weird_val, $num_weird_val,$min_diff, $max_diff, $tot_diff, $min_percent, $max_percent, $tot_err_percent, $rse, $num_items, $num_diffs, $av_faulty_value, $av_golden_value, $av_rel_err, $timing_val_mismatch, $t_weird_val, $t_num_weird_val,$t_min_diff, $t_max_diff, $t_tot_diff, $t_min_percent, $t_max_percent, $t_tot_err_percent, $t_rse, $t_num_items, $t_num_diffs, $t_av_faulty_value, $t_av_golden_value, $t_av_rel_err, $max_faulty_val, $min_faulty_val );

	}

} 
elsif ($app_name eq "lu_reduced" || $app_name eq "lu_run_input_0" || $app_name eq "lu_run_full" || $app_name =~ /lu/) {
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} 
	else
	{
		my $acceptability = 1000;
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my ($num_weird_val, $weird_val, $legit_val, $g_val_zero, $g_val_zero_num) = 0;
		my ($num_diffs, $rse, $num_items, $av_faulty_value, $av_golden_value, $av_rel_err) = 0;
		#my $num_tot = 0;
		my ($tot_diff, $tot_err_percent, $tot_se, $tot_faulty_value, $tot_golden_value)=0; 
		my ($min_diff, $max_diff, $min_percent, $max_percent, $average);
		my ($max_faulty_val, $min_faulty_val)= 0;
		my ($upper_se, $lower_se, $diag_se) = 0;
		my ($upper_se_golden, $lower_se_golden, $diag_se_golden) = 0; # calculate diagonal seperately (not sure it belongs to upper or lower)
		#temporary-calc
		#my ($tot_golden_se, $tot_golden_rse) = 0;
		#end temporary_calc

		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;
		my ($col_mismatch,$g_val, $f_val) = 0;
		
		my @A_orig;
		my @A;
		my @B;
		my ($A_row, $A_col, $B_row, $B_col) = (0, 0, 0, 0);
		my $start = 0;
		my $start_orig = 0;
		if($#g_lines != $#f_lines) {
			$acceptability = "Eggregious-line_num_mismatch";
			#$eggregious = 1;
		} else
		{
			foreach $i (0 .. $#g_lines) 
			{ 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];


				if($g_line =~ /Matrix before decomposition:/) {
					$start_orig = 1;
					($A_row, $A_col, $B_row, $B_col) = (0, 0, 0, 0);
					next;
				}

				if($g_line =~ /Matrix after decomposition:/) {
					$start = 1;
					$start_orig = 0;
					($A_row, $A_col, $B_row, $B_col) = (0, 0, 0, 0);
					next;
				}
				if($g_line =~ /PROCESS STATISTICS/) {
					$start = 0;
					next;
				}

				if($start_orig == 1) {
					$A_col = 0;
					chomp($g_line);
					my @g_words = split(/\s+/,$g_line);
					foreach $g_word (@g_words) { 
						if($g_word ne "") {
							$A_orig[$A_row][$A_col] = $g_word;
							$A_col++;
							# print "$g_word-";
						}
					}
					$A_row++;
				}

				if($start == 1) {
					$A_col = 0;
					$B_col = 0;
					chomp($g_line);
					chomp($f_line);
					my @g_words = split(/\s+/,$g_line);
					my @f_words = split(/\s+/,$f_line);
					if ($#g_words == $#f_words) {
						foreach $g_word (@g_words) { 
							if($g_word ne "") {
								$A[$A_row][$A_col] = $g_word;
								#radha
								#printf ("Radha : %d, %d, %f\n", $A_row, $A_col, $g_word);
								#end_radha
								$A_col++;
								# print "$g_word-";
							}
						}
						#print "\n";
						foreach $f_word (@f_words) { 
							if($f_word ne "") {
								$B[$B_row][$B_col] = $f_word;
								$B_col++;
							}
						}
					}
					else
					{
						$col_mismatch = 1;
					}
					$A_row++;
					$B_row++;
				}
			}#end of foreach

			if (($A_row != $B_row) or ($col_mismatch == 1))
			{
				$acceptability = "Eggregious-row_column_number_mismatch";	
			}
			else
			{
				foreach $j (0 .. $A_row-1)
				{
					foreach $k (0 .. $A_col-1)
					{
						$g_val = $A[$j][$k]; 
						$f_val = $B[$j][$k];
						$tot_golden_value += $g_val;
						$tot_faulty_value += $f_val;
						$num_items++;
						#seperate the upper and lower triangular matrix se
						if($j == $k)
						{
							$diag_se_golden += ($g_val*$g_val);
						}
						elsif($j < $k)
						{
							$upper_se_golden += ($g_val*$g_val);
						}
						else # j > k
						{
							$lower_se_golden += ($g_val*$g_val);
						}
						#radha
						#printf("Radha %d, %d, %d, %f, %f\n", $j, $k, $num_items, $g_val, $f_val);
						#radha_end

						#temporary-calc
						#my $temp_golden_se = ($g_val*$g_val);
						#$tot_golden_se += $temp_golden_se;
						#end_temporary-calc	
						if ($g_val != $f_val)
						{
							$num_diffs++;
							#printf ("%d, %d\n", $j, $k);
							#normal values in the outputs are numeric. Log if there is anything else that is weird.(Nan, Infinity, alphanumeric)
		
							if(not looks_like_number($f_val) or ($f_val =~ /[a-zA-Z]/))
							{
								#print "WEIRD VALUE\n";
								$num_weird_val++;
								$weird_val = 1;
								$legit_val = 0;
							}
							else
							{
								$legit_val = 1
							}

							if ($legit_val == 1)
							{
								my $diff = &get_abs_diff($g_val, $f_val);
								#print "4: $diff,$g_val, $f_val \n";
								#some of the g_val is negetive. So take the absolute value
								my $err_percent = abs(&get_error_percent($g_val, $diff));
								my $se = ($diff*$diff); #square error
								$tot_diff += $diff;
								$tot_err_percent += $err_percent;
								$tot_se += $se;
								# add the se for upper and lower matrix
								if($j == $k)
								{
									$diag_se += $se;
								}
								elsif($j < $k)
								{
									$upper_se += $se;
								}
								else # j > k
								{
									$lower_se += $se;
								}

								if ($num_diffs == 1)
								{
									$min_diff = $diff;
									$max_diff = $diff;
									$min_percent = $err_percent;
									$max_percent = $err_percent;
									$max_faulty_val = $f_val;
									$min_faulty_val = $f_val;	
								}
								else
								{
									$min_diff = &get_min($diff, $min_diff);
									$max_diff = &get_max($diff, $max_diff);
									$min_percent = &get_min($err_percent, $min_percent);
									$max_percent = &get_max($err_percent, $max_percent);
									$max_faulty_val = &get_max($f_val, $max_faulty_val);
									$min_faulty_val = &get_min($f_val, $min_faulty_val);

								}
							}


						}
						# end of the $g_val!=f_val
						#printf ("%d, %d ,g_val : %0.2f, f_val : %0.2f, %0.2f, %0.2f, %0.2f, %0.2f, %0.2f\n", $j, $k, $g_val, $f_val, $diff, $min_diff, $max_diff, $min_percent, $max_percent );
					}
				} #end of foreach
				$rse = sqrt($tot_se);
				#temporary-calc
				#$tot_golden_rse = sqrt($tot_golden_se);
				#end temporary_calc
				$av_faulty_value = ($tot_faulty_value/$num_items);
				$av_golden_value = ($tot_golden_value/$num_items);
				my $av_diff = &get_abs_diff($av_golden_value, $av_faulty_value);
				$av_rel_err = &get_error_percent($av_golden_value, $av_diff); 

				$acceptability = "Tolerable";	

			}#end of if-else


		}#big end of else

		printf ("SDC:%s;%d,%d,%.10f,%.10f,%.10f,%f,%f,%f,%.10f,%d,%d,%.10f,%.10f,%f,%f,%f,%f,%f,%f,%f,%f,%f \n",$acceptability, $weird_val, $num_weird_val, $min_diff, $max_diff, $tot_diff, $min_percent, $max_percent, $tot_err_percent, $rse, $num_items, $num_diffs, $av_faulty_value, $av_golden_value, $av_rel_err, $max_faulty_val, $min_faulty_val, $upper_se_golden, $lower_se_golden, $diag_se_golden, $upper_se, $lower_se, $diag_se);	

	} #end of else to "Masked"

}
elsif ($app_name eq "fft_small" || $app_name eq "fft_run_0" 
    || $app_name eq "fft_run_1" 
    || $app_name eq "fft_run_2" 
    || $app_name eq "fft_run_3" 
    || $app_name eq "fft_run_4" 
    || $app_name eq "fft_run_5" 
    || $app_name eq "fft_run_6" 
    || $app_name =~ /fft/
    )
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} 
	else 
	{
		my $acceptability = 1000;
		#Radha
		#print "I am here\n";
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my ($num_weird_val, $weird_val, $legit_val, $g_val_zero, $g_val_zero_num) = 0;
		my ($num_diffs, $rse, $num_items, $av_faulty_value, $av_golden_value, $av_rel_err) = 0;
		#my $num_tot = 0;
		my ($tot_diff, $tot_err_percent, $tot_se, $tot_faulty_value, $tot_golden_value)=0; 
		my ($min_diff, $max_diff, $min_percent, $max_percent, $average);
		my ($max_faulty_val, $min_faulty_val)= 0;
		#temporary-calc
		#my ($tot_golden_se, $tot_golden_rse) = 0;
		#end temporary_calc


		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		my @A_orig;
		my @A;
		my @B;
		my ($A_index, $B_index) = (0, 0);
		my $start = 0;
		my $start_orig = 0;
		#Radha
		#print "Num : $#g_lines, $#f_lines\n";
		if($#g_lines != $#f_lines) {
			$acceptability = "Eggregious-line_num_mismatch";
			#$eggregious = 1;
		} 
		else
		{

			#Radha
			#print "I am herei 2\n";
			foreach $i (0 .. $#g_lines) 
			{ 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];

				#Radha
				#print "G : $g_line\n";
				#print "F : $f_line\n";

				if($g_line =~ /Original data values:/) {
					#Radha
					#print "Original data structure\n";
					$start_orig = 1;
					($A_index, $B_index) = (0, 0);
					next;
				}

				if($g_line =~ /Data values after FFT:/) {
					#Radha 
					#print "Data values after\n";
					$start = 1;
					$start_orig = 0;
					($A_index, $B_index) = (0, 0);
					next;
				}
				if($g_line =~ /PROCESS STATISTICS/) {
					#Radha
					#print "In Process statistics\n";
					$start = 0;
					next;
				}

				if($start_orig == 1) {
					#Radha
					#print "In start_orig == 1\n";
					chomp($g_line);
					my @g_words = split(/,/,$g_line);
					foreach $g_word (@g_words) { 
						if($g_word ne "") {
							my @complex_num = split(/\s+/,$g_word);
							#print "$A_index:";
							#print "$complex_num[0]-$complex_num[1]-";
							#print "$complex_num[2]-$complex_num[3]-\n";
							$A_orig[$A_index] = $complex_num[1];
							$A_orig[$A_index+1] = $complex_num[2];
							$A_index += 2;
							#Radha
							#print "Hello $A_index\n";
						}
					}
				}

				#Radha
				#print "I am here 5 $A_index $B_index\n";

				if($start == 1) {
					chomp($g_line);
					chomp($f_line);
					my @g_words = split(/,/,$g_line);
					my @f_words = split(/,/,$f_line);
					
					if ($#g_words == $#f_words) {
						foreach $g_word (@g_words) { 
							if($g_word ne "") {
								my @complex_num = split(/\s+/,$g_word);
								$A[$A_index] = $complex_num[1];
								$A[$A_index+1] = $complex_num[2];
								$A_index += 2;
							}
						}
						#print "\n";
						foreach $f_word (@f_words) { 
							if($f_word ne "") {
								my @complex_num = split(/\s+/,$f_word);
								$B[$B_index] = $complex_num[1];
								$B[$B_index+1] = $complex_num[2];
								$B_index += 2;
							}
						}
					}
				}
			} #end of foreach

			#Radha
			#print "I am here 3\n";
			if ($A_index != $B_index)
			{
				$acceptability = "Eggregious-index_number_mismatch";	
			}
			else
			{

				#Radha
				#print "I am here 4 $A_index $B_index\n";
				foreach $j (0 .. $A_index)
				{
					$g_val = $A[$j]; 
					$f_val = $B[$j];
					$tot_golden_value += $g_val;
					$tot_faulty_value += $f_val;
					$num_items++;
					#temporary-calc
					#my $temp_golden_se = ($g_val*$g_val);
					#$tot_golden_se += $temp_golden_se;
					#end_temporary-calc	
					if ($g_val != $f_val)
					{
						$num_diffs++;
						#printf ("%d, %d, %d, %d\n", $g_val, $f_val, $num_diffs);
						#normal values in the outputs are numeric. Log if there is anything else that is weird.(Nan, Infinity, alphanumeric)
						if(not looks_like_number($f_val) or ($f_val =~ /[a-zA-Z]/))
						{
				#			print "WEIRD VALUE $g_val $f_val\n";
							$num_weird_val++;
							$weird_val = 1;
							$legit_val = 0;
						}
						else
						{
							$legit_val = 1
						}

						if ($legit_val == 1)
						{
							my $diff = &get_abs_diff($g_val, $f_val);
							#print "4: $diff,$g_val, $f_val \n";
							#some of the g_val is negetive. So take the absolute value
							my $err_percent = abs(&get_error_percent($g_val, $diff));
							my $se = ($diff*$diff); #square error
							$tot_diff += $diff;
							$tot_err_percent += $err_percent;
							$tot_se += $se;

							if ($num_diffs == 1)
							{
								$min_diff = $diff;
								$max_diff = $diff;
								$min_percent = $err_percent;
								$max_percent = $err_percent;
								$max_faulty_val = $f_val;
								$min_faulty_val = $f_val;	
							}
							else
							{
								$min_diff = min($diff, $min_diff); #&get_min($diff, $min_diff);
								$max_diff = max($diff, $max_diff); #&get_max($diff, $max_diff);
								$min_percent = min($err_percent, $min_percent); #&get_min($err_percent, $min_percent);
								$max_percent = max($err_percent, $max_percent); #&get_max($err_percent, $max_percent);
								$max_faulty_val = max($f_val, $max_faulty_val); #&get_max($f_val, $max_faulty_val);
								$min_faulty_val = min($f_val, $min_faulty_val); #&get_min($f_val, $min_faulty_val);

							}
						}


					}
				} #end of foreach
				$rse = sqrt($tot_se);
				#temporary-calc
				#$tot_golden_rse = sqrt($tot_golden_se);
				#end temporary_calc
				$av_faulty_value = ($tot_faulty_value/$num_items);
				$av_golden_value = ($tot_golden_value/$num_items);
				my $av_diff = &get_abs_diff($av_golden_value, $av_faulty_value);
				$av_rel_err = &get_error_percent($av_golden_value, $av_diff); 

				$acceptability = "Tolerable";	
			} #end of else

		} #end of tolerable else

		printf ("SDC:%s;%d,%d,%.10f,%.10f,%.10f,%f,%f,%f,%.10f,%d,%d,%.10f,%.10f,%f,%f,%f\n",$acceptability, $weird_val, $num_weird_val, $min_diff, $max_diff, $tot_diff, $min_percent, $max_percent, $tot_err_percent, $rse, $num_items, $num_diffs, $av_faulty_value, $av_golden_value, $av_rel_err, $max_faulty_val, $min_faulty_val);		


	} #end of sdc else

} #end of app
elsif ($app_name eq "streamcluster_simsmall" || $app_name =~ /streamcluster/)
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} 
	else 
	{
		my $acceptability = 1000;
		#Radha
		#print "I am here\n";
# 		open both files and check vlaues line by line
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my ($num_weird_val, $weird_val, $legit_val, $g_val_zero, $g_val_zero_num, $negetive_val) = 0;
		my ($num_diffs, $rse, $num_items, $av_faulty_value, $av_golden_value, $av_rel_err) = 0;
		#my $num_tot = 0;
		my ($tot_diff, $tot_err_percent, $tot_se, $tot_faulty_value, $tot_golden_value)=0; 
		my ($min_diff, $max_diff, $min_percent, $max_percent, $average);
		my ($max_faulty_val, $min_faulty_val)= 0;
		#temporary-calc
		#my ($tot_golden_se, $tot_golden_rse) = 0;
		#end temporary_calc


		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		my @A;
		my @B;
		my ($A_index, $B_index) = (0, 0);
		if($#g_lines != $#f_lines) {
			$acceptability = "Eggregious-line_num_mismatch";
			#$eggregious = 1;
		} 
		else
		{

			foreach $i (0 .. $#g_lines) 
			{ 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];

				
				chomp($g_line);
				chomp($f_line);
				my @g_words = split(/\s+/,$g_line);
				my @f_words = split(/\s+/,$f_line);
				
				if ($#g_words == $#f_words) {
					foreach $g_word (@g_words) { 
						if($g_word ne "") {
							$A[$A_index] = $g_word;
							$A_index += 1;
							#printf("%d, %f, %f\n", $A_index, $g_word, $A[$A_index-1]);
						}
					}
					#print "\n";
					foreach $f_word (@f_words) { 
						if($f_word ne "") {
							$B[$B_index] = $f_word;
							$B_index += 1;
						}
					}
				}
			} #end of foreach

			#Radha
			#print "I am here 3\n";
			if ($A_index != $B_index)
			{
				$acceptability = "Eggregious-index_number_mismatch";	
			}
			else
			{

				#Radha
				#print "I am here 4 $A_index $B_index\n";
				foreach $j (0 .. ($A_index-1))
				{
					$g_val = $A[$j]; 
					$f_val = $B[$j];
					$tot_golden_value += $g_val;
					$tot_faulty_value += $f_val;
					$num_items++;
					#temporary-calc
					#my $temp_golden_se = ($g_val*$g_val);
					#$tot_golden_se += $temp_golden_se;
					#end_temporary-calc	
					if ($g_val != $f_val)
					{
						$num_diffs++;
						#printf ("%d, %d, %d, %d\n", $g_val, $f_val, $num_diffs);
						#normal values in the outputs are numeric. Log if there is anything else that is weird.(Nan, Infinity, alphanumeric)
						if(not looks_like_number($f_val) or ($f_val =~ /[a-zA-Z]/))
						{
							#print "WEIRD VALUE $g_val $f_val\n";
							$num_weird_val++;
							$weird_val = 1;
							$legit_val = 0;
						}
						else
						{
							$legit_val = 1
						}
						if($f_val != abs($f_val))
						{
							$negetive_val = 1;
						}
						if ($legit_val == 1)
						{
							my $diff = &get_abs_diff($g_val, $f_val);
							#print "4: $diff,$g_val, $f_val \n";
							#some of the g_val is negetive. So take the absolute value
							my $err_percent = abs(&get_error_percent($g_val, $diff));
							my $se = ($diff*$diff); #square error
							$tot_diff += $diff;
							$tot_err_percent += $err_percent;
							$tot_se += $se;

							if ($num_diffs == 1)
							{
								$min_diff = $diff;
								$max_diff = $diff;
								$min_percent = $err_percent;
								$max_percent = $err_percent;
								$max_faulty_val = $f_val;
								$min_faulty_val = $f_val;	
							}
							else
							{
								$min_diff = &get_min($diff, $min_diff);
								$max_diff = &get_max($diff, $max_diff);
								$min_percent = &get_min($err_percent, $min_percent);
								$max_percent = &get_max($err_percent, $max_percent);
								$max_faulty_val = &get_max($f_val, $max_faulty_val);
								$min_faulty_val = &get_min($f_val, $min_faulty_val);

							}
						}


					}
				} #end of foreach
				$rse = sqrt($tot_se);
				#temporary-calc
				#$tot_golden_rse = sqrt($tot_golden_se);
				#end temporary_calc
				$av_faulty_value = ($tot_faulty_value/$num_items);
				$av_golden_value = ($tot_golden_value/$num_items);
				my $av_diff = &get_abs_diff($av_golden_value, $av_faulty_value);
				$av_rel_err = &get_error_percent($av_golden_value, $av_diff); 

				$acceptability = "Tolerable";	
			} #end of else

		} #end of tolerable else

		printf ("SDC:%s;%d,%d,%.10f,%.10f,%.10f,%f,%f,%f,%.10f,%d,%d,%.10f,%.10f,%f,%f,%f,%d\n",$acceptability, $weird_val, $num_weird_val, $min_diff, $max_diff, $tot_diff, $min_percent, $max_percent, $tot_err_percent, $rse, $num_items, $num_diffs, $av_faulty_value, $av_golden_value, $av_rel_err, $max_faulty_val, $min_faulty_val, $negetive_val);		


	} #end of sdc else

} 
elsif ($app_name =~ /ctaes/)
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	}
	else
	{
		open IN_GF, "<$golden_file";
		open IN_FF, "<$output_file";
		my $weird_val = 0;
		my $line_mismatch = 0;
		my $num_char_mismatch = 0;
		my @g_lines = <IN_GF>;
		my @f_lines = <IN_FF>;
		close IN_GF;
		close IN_FF;

		if($#g_lines != $#f_lines) {
			$line_mismatch = 1;
			#$eggregious = 1;
		} 
		else
		{

			foreach $i (0 .. $#g_lines) 
			{ 
				my $g_line = $g_lines[$i];
				my $f_line = $f_lines[$i];
				chomp($g_line);
				chomp($f_line);

				if (length($g_line) != length($f_line))
				{
					$num_char_mismatch = 1;	
				}
				if ($f_line =~ m/[^a-fA-F0-9]/) #anything other than alpha-numeric
				{
					$weird_val = 1;
				}
			}
		}
		printf ("SDC:Egregious;%d,%d,%d\n",$line_mismatch,$num_char_mismatch,$weird_val);
	} 
}#end of app
if($app_name =~ /sobel/ || $app_name  =~ /jpeg/ || $app_name =~ /kmeans/ )
{
	my $golden_file = "$GOLDEN_DIR/$app_name.output";
	$result = `diff -q $output_file $golden_file`;
	if ($result eq "") {
		print "Masked\n";
	} else {
        
        if ($app_name =~ /kmeans/ ) {
           system("python $SCRIPTS_DIR/convert.py $output_file out_$id.jpg\n");
           $output = `python $SCRIPTS_DIR/rmse.py $GOLDEN_DIR/$app_name.jpg out_$id.jpg`;
           system("rm -f out_$id.jpg\n");
        }
        else {
            $output = `python $SCRIPTS_DIR/rmse.py $golden_file $output_file`;
	    }
        printf ("%s",$output);
        `deactivate`;
		# print "number of differences = $num_diffs\n";
	}
} #end of app

 

