model HeatCapacity_TableTopExperiment_MaterialSelection
  import Modelica.Units.SI;
  // =========================================================
  // 1. PARAMETER SECTION
  // =========================================================
  parameter SI.Length a_Wuerfel = 0.035 "Edge length of the cube (35mm)";
  final parameter SI.Volume V_Wuerfel = a_Wuerfel^3 "Calculated volume";
  parameter Integer materialSelection = 1 "Select material" annotation(
    choices(choice = 1 "Aluminium", choice = 2 "Copper", choice = 3 "Steel"));
  final parameter SI.Mass m_Wuerfel = if materialSelection == 1 then 0.113 else if materialSelection == 2 then 0.377 else 0.339;
  final parameter SI.SpecificHeatCapacity c_eff_Wuerfel = if materialSelection == 1 then 897 else if materialSelection == 2 then 385 else 470;
  parameter SI.Mass m_Wasser = 0.300 "Water mass (300g)";
  parameter SI.SpecificHeatCapacity c_Wasser = 4182 "Specific heat cap. water";
  parameter SI.HeatCapacity C_Gefaess = 50 "Water equivalent of the thermos (C_VESSEL)";
  parameter SI.Temperature T_Umgebung = 295.15 "Laboratory ambient temperature (22 °C)";
  parameter SI.Temperature T_Wasser_Start = 295.15 "Water start temperature (22 °C)";
  parameter SI.Temperature T_Wuerfel_Start = 333.15 "Cube start temperature (60 °C)";
  parameter SI.ThermalConductance G_Isolation = 0.187 "Conductance of the cup insulation (K_VALUE)";
  // CALIBRATED: An alpha_A of 3.5 achieves equilibrium for aluminum in approx. 110 seconds
  parameter Real alpha_A_Konvektion = 3.5 "Heat transfer alpha * A (cube to water)";
  // =========================================================
  // LIVE EVALUATION VARIABLES
  // =========================================================
  Real E_loss(start = 0, fixed = true) "Integrated heat loss (J)";
  Real delta_T_w "Temperature change water (K)";
  Real delta_T_e "Temperature change sample (K)";
  Real Q_Wasser "Energy change water (J)";
  Real Q_Probe "Energy change sample (J)";
  Real c_berechnet_kg "Live calculated heat capacity J/(kg*K)";
  Real c_berechnet_g "Live calculated heat capacity J/(g*K) - like in Dash App";
  // =========================================================
  // 2. COMPONENT DECLARATION
  // =========================================================
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor Cube(C = m_Wuerfel*c_eff_Wuerfel, T(start = T_Wuerfel_Start, fixed = true)) annotation(
    Placement(transformation(origin = {-60, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor Water(C = m_Wasser*c_Wasser, T(start = T_Wasser_Start, fixed = true)) annotation(
    Placement(transformation(origin = {24, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor Cup(C = C_Gefaess, T(start = T_Wasser_Start)) annotation(
    Placement(transformation(origin = {4, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection konvektion annotation(
    Placement(transformation(origin = {-20, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant alpha_A(k = alpha_A_Konvektion) annotation(
    Placement(transformation(origin = {-50, 62}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor r_loss(G = G_Isolation) annotation(
    Placement(transformation(origin = {60, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature ambient(T = T_Umgebung) annotation(
    Placement(transformation(origin = {100, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor sensorCube annotation(
    Placement(transformation(origin = {-38, -8}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor sensorWater annotation(
    Placement(transformation(origin = {52, -16}, extent = {{-10, -10}, {10, 10}})));
equation
// =========================================================
// 3. CONNECTIONS
// =========================================================
  connect(alpha_A.y, konvektion.Gc) annotation(
    Line(points = {{-39, 62}, {-39, 38.5}, {-20, 38.5}, {-20, 28}}));
  connect(Cube.port, konvektion.solid) annotation(
    Line(points = {{-50, 20}, {-30, 20}}));
  connect(konvektion.fluid, Water.port) annotation(
    Line(points = {{-10, 20}, {24, 20}}));
  connect(Water.port, Cup.port) annotation(
    Line(points = {{24, 20}, {24, -10}, {4, -10}, {4, -40}}));
  connect(Water.port, r_loss.port_a) annotation(
    Line(points = {{24, 20}, {50, 20}}));
  connect(r_loss.port_b, ambient.port) annotation(
    Line(points = {{70, 20}, {90, 20}}));
  connect(Cube.port, sensorCube.port) annotation(
    Line(points = {{-60, 10}, {-60, -8}, {-48, -8}}));
  connect(Water.port, sensorWater.port) annotation(
    Line(points = {{24, 20}, {24, -17}, {42, -17}, {42, -16}}));
// =========================================================
// 4. LIVE EVALUATION (Analog to Python)
// =========================================================
// Integrate heat loss (der() is the time derivative)
  der(E_loss) = G_Isolation*(sensorWater.T - T_Umgebung);
// Calculate Delta T
  delta_T_w = T_Wasser_Start - sensorWater.T;
  delta_T_e = sensorCube.T - T_Wuerfel_Start;
// Energy balance
  Q_Wasser = (m_Wasser*c_Wasser + C_Gefaess)*delta_T_w;
  Q_Probe = Q_Wasser - E_loss;
// Calculate heat capacity
  c_berechnet_kg = if abs(delta_T_e) > 0.5 then Q_Probe/(m_Wuerfel*delta_T_e) else 0.0;
// Conversion to J/(g*K), matching Dash app display
  c_berechnet_g = c_berechnet_kg/1000;
  annotation(
    Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {// Base: Groove plate
    Rectangle(extent = {{-90, -90}, {90, -75}}, lineColor = {120, 120, 120}, fillColor = {190, 190, 190}, fillPattern = FillPattern.Solid), Line(points = {{-60, -90}, {-60, -75}}, color = {150, 150, 150}), Line(points = {{-30, -90}, {-30, -75}}, color = {150, 150, 150}), Line(points = {{0, -90}, {0, -75}}, color = {150, 150, 150}), Line(points = {{30, -90}, {30, -75}}, color = {150, 150, 150}), Line(points = {{60, -90}, {60, -75}}, color = {150, 150, 150}), // Mechanics tower
    Rectangle(extent = {{-85, -75}, {-65, 80}}, lineColor = {80, 80, 80}, fillColor = {160, 160, 160}, fillPattern = FillPattern.Solid), Rectangle(extent = {{-85, 60}, {20, 75}}, lineColor = {80, 80, 80}, fillColor = {160, 160, 160}, fillPattern = FillPattern.Solid), // Calorimeter (Double-walled)
    Rectangle(extent = {{-40, 30}, {40, -70}}, lineColor = {0, 0, 0}, lineWidth = 1), Rectangle(extent = {{-35, 28}, {35, -66}}, lineColor = {150, 150, 150}, lineWidth = 0.5), // Water content
    Rectangle(extent = {{-34, -10}, {34, -65}}, lineColor = {0, 120, 255}, fillColor = {180, 220, 255}, fillPattern = FillPattern.Solid), // Stirrer unit
    Line(points = {{0, 65}, {0, -45}}, color = {0, 0, 0}, thickness = 1), Rectangle(extent = {{-12, -45}, {12, -52}}, lineColor = {50, 50, 50}, fillColor = {100, 100, 100}, fillPattern = FillPattern.Solid), // Sample cube
    Rectangle(extent = {{10, -25}, {30, -45}}, lineColor = {0, 0, 0}, fillColor = {130, 130, 130}, fillPattern = FillPattern.Solid), Ellipse(extent = {{18, -33}, {22, -37}}, lineColor = {0, 0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid), // Sensor bore
// Wiring (Indication)
    Line(points = {{-10, 65}, {-10, 5}, {15, 5}, {15, -25}}, color = {255, 0, 0}, thickness = 0.5), // Labeling
    Text(extent = {{-100, -100}, {100, -85}}, textString = "%name", lineColor = {0, 0, 0}), Text(extent = {{-100, 100}, {100, 85}}, textString = "Digital Twin: Heat Capacity", lineColor = {50, 50, 50})}),
    uses(Modelica(version = "4.0.0")),
    experiment(StartTime = 0, StopTime = 3600, Tolerance = 1e-06, Interval = 1.8),
    Diagram(coordinateSystem(extent = {{-80, 80}, {120, -40}})),
    version = "",
  Documentation);
end HeatCapacity_TableTopExperiment_MaterialSelection;
